"""Genera dashboard visual de conclusiones y relaciones del proyecto.

Usa DuckDB + matplotlib para crear graficos esquematicos.
Guarda PNGs en data/resultados/ y un MD resumen.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"
OUT = PROJECT_ROOT / "data" / "resultados"
OUT.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")


def _save(fig, name):
    p = OUT / name
    fig.savefig(p, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {p}")
    return p


def g1_esfuerzo_territorio():
    df = duckdb.query("""
        SELECT territorio, esfuerzo_min_pct, esfuerzo_max_pct
        FROM read_csv('data/procesado/dim_municipios_enriquecido.csv')
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    data = df.melt(id_vars="territorio", value_vars=["esfuerzo_min_pct", "esfuerzo_max_pct"],
                   var_name="proxy", value_name="esfuerzo")
    data["proxy"] = data["proxy"].map({"esfuerzo_min_pct": "Salarial (min)", "esfuerzo_max_pct": "Fiscal (max)"})
    sns.boxplot(data=data, x="territorio", y="esfuerzo", hue="proxy", ax=ax)
    ax.axhline(30, color="red", linestyle="--", label="Umbral 30%")
    ax.set_title("Esfuerzo de alquiler por territorio (min/max)")
    ax.set_ylabel("Esfuerzo (%)")
    ax.set_xlabel("")
    ax.legend(title="Proxy")
    return _save(fig, "g1_esfuerzo_territorio.png")


def g2_renta_vs_alquiler():
    df = duckdb.query("""
        SELECT renta_personal_total_eur, alquiler_anual_calc, territorio, tipologia_mercado
        FROM read_csv('data/procesado/dim_municipios_enriquecido.csv')
        WHERE alquiler_anual_calc IS NOT NULL
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x="renta_personal_total_eur", y="alquiler_anual_calc",
                    hue="territorio", style="tipologia_mercado", ax=ax, alpha=0.7)
    ax.set_title("Renta personal total vs Alquiler anual por municipio")
    ax.set_xlabel("Renta personal total (EUR/anio)")
    ax.set_ylabel("Alquiler anual (EUR)")
    return _save(fig, "g2_renta_vs_alquiler.png")


def g3_top10_precio():
    df = duckdb.query("""
        SELECT municipio, ROUND(MEDIAN(precio_eur),0) AS precio_medio, COUNT(*) AS n
        FROM read_csv('data/procesado/anuncios_vivienda_residencial_filtrado.csv')
        WHERE outlier = FALSE
        GROUP BY municipio
        ORDER BY precio_medio DESC
        LIMIT 10
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df, x="precio_medio", y="municipio", ax=ax, palette="Reds_r")
    ax.set_title("Top 10 municipios por precio mediano de alquiler (datos filtrados)")
    ax.set_xlabel("Precio medio (EUR/mes)")
    ax.set_ylabel("")
    return _save(fig, "g3_top10_precio.png")


def g4_distribucion_anuncios():
    df = duckdb.query("""
        SELECT n_anuncios, tipologia_mercado
        FROM read_csv('data/procesado/analisis_variables_base.csv')
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df, x="n_anuncios", hue="tipologia_mercado", bins=30, ax=ax, multiple="stack")
    ax.set_title("Distribucion de anuncios por municipio (robustez)")
    ax.set_xlabel("Nº anuncios")
    ax.set_ylabel("Nº municipios")
    return _save(fig, "g4_distribucion_anuncios.png")


def g5_esfuerzo_ranking():
    df = duckdb.query("""
        SELECT nombre_canonico, territorio, esfuerzo_min_pct, esfuerzo_max_pct, n_anuncios
        FROM read_csv('data/procesado/dim_municipios_enriquecido.csv')
        WHERE n_anuncios >= 30
        ORDER BY esfuerzo_min_pct
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(df))
    ax.barh(df["nombre_canonico"], df["esfuerzo_min_pct"], color="steelblue", label="Esfuerzo min (salarial)")
    ax.barh(df["nombre_canonico"], df["esfuerzo_max_pct"], color="salmon", alpha=0.5, label="Esfuerzo max (fiscal)")
    ax.axvline(30, color="red", linestyle="--", label="Umbral 30%")
    ax.set_title("Esfuerzo por municipio robusto (n>=30)")
    ax.set_xlabel("Esfuerzo (%)")
    ax.legend()
    return _save(fig, "g5_esfuerzo_robustos.png")


def main():
    print("Generando graficos...")
    g1_esfuerzo_territorio()
    g2_renta_vs_alquiler()
    g3_top10_precio()
    g4_distribucion_anuncios()
    g5_esfuerzo_ranking()
    print(f"\n5 graficos guardados en {OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
