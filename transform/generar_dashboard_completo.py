"""Genera dashboard visual completo: 7 bloques (A-G) con graficos y conclusiones.

Usa DuckDB + matplotlib. Guarda PNGs en data/resultados/ y dashboard.html.
Regenerable con: python transform/generar_dashboard_completo.py
"""
from __future__ import annotations

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


def g_A1_esfuerzo_territorio():
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
    ax.set_title("A1-A3: Esfuerzo de alquiler por territorio (min/max)")
    ax.set_ylabel("Esfuerzo (%)")
    ax.set_xlabel("")
    ax.legend(title="Proxy")
    return _save(fig, "A1_esfuerzo_territorio.png")


def g_A2_municipios_inasequibles():
    df = duckdb.query("""
        SELECT territorio,
               SUM(CASE WHEN esfuerzo_min_pct > 30 THEN 1 ELSE 0 END) AS n_inaseq,
               COUNT(*) AS n_total
        FROM read_csv('data/procesado/dim_municipios_enriquecido.csv')
        GROUP BY territorio
    """).df()
    df["pct"] = (df["n_inaseq"] / df["n_total"] * 100).round(1)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df, x="territorio", y="pct", ax=ax, palette="Reds")
    ax.set_title("A2: % municipios con esfuerzo >30% (inasequible)")
    ax.set_ylabel("% municipios")
    ax.set_xlabel("")
    for i, v in enumerate(df["pct"]):
        ax.text(i, v + 1, f"{v}%", ha="center")
    return _save(fig, "A2_municipios_inasequibles.png")


def g_B_paro_vs_precio():
    df = duckdb.query("""
        SELECT a.nombre_canonico AS municipio, a.tasa_paro_lanbide_pct, b.precio_medio, a.territorio
        FROM read_csv('data/procesado/analisis_variables_base.csv') a
        JOIN (
            SELECT municipio, MEDIAN(precio_eur) AS precio_medio
            FROM read_csv('data/procesado/anuncios_vivienda_residencial_filtrado.csv')
            WHERE outlier = FALSE
            GROUP BY municipio
        ) b ON a.nombre_canonico = b.municipio
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x="tasa_paro_lanbide_pct", y="precio_medio",
                    hue="territorio", ax=ax, alpha=0.7)
    ax.set_title("B1-B4: Paro juvenil (Lanbide) vs Precio alquiler (anuncios)")
    ax.set_xlabel("Tasa paro Lanbide (%)")
    ax.set_ylabel("Precio medio anuncios (EUR)")
    return _save(fig, "B_paro_vs_precio.png")


def g_C_vpo_antiguedad():
    df = duckdb.query("""
        SELECT a.territorio,
               AVG(b.vpo_terminadas_por_mil) AS vpo_media,
               AVG(a.antiguedad_media_anyos) AS antiguedad_media
        FROM read_csv('data/procesado/analisis_variables_base.csv') a
        JOIN read_csv('data/procesado/udalmap_empleo_corregido.csv') b
          ON a.codigo_ine = b.codigo_ine
        GROUP BY a.territorio
    """).df()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=df, x="territorio", y="vpo_media", ax=axes[0], palette="Blues")
    axes[0].set_title("C1: VPO terminadas (%) por territorio")
    axes[0].set_ylabel("VPO %")
    axes[0].set_xlabel("")
    sns.barplot(data=df, x="territorio", y="antiguedad_media", ax=axes[1], palette="Oranges")
    axes[1].set_title("C2: Viviendas >50 años (%) por territorio")
    axes[1].set_ylabel("% viviendas >50 años")
    axes[1].set_xlabel("")
    return _save(fig, "C_vpo_antiguedad.png")


def g_D_distancia_precio():
    df = duckdb.query("""
        SELECT nombre_canonico, territorio, dist_centroide_comarca_km,
               renta_media_eur_m2_media, tipologia_mercado
        FROM read_csv('data/procesado/analisis_variables_base.csv')
        WHERE renta_media_eur_m2_media IS NOT NULL
    """).df()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x="dist_centroide_comarca_km", y="renta_media_eur_m2_media",
                    hue="territorio", style="tipologia_mercado", ax=ax, alpha=0.6)
    ax.set_title("D1-D4: Distancia a comarca vs Precio alquiler (EUR/m2)")
    ax.set_xlabel("Distancia a centroide comarca (km)")
    ax.set_ylabel("Precio medio alquiler (EUR/m2)")
    return _save(fig, "D_distancia_precio.png")


def g_E_demografia():
    df = duckdb.query("""
        SELECT a.territorio,
               AVG(CAST(b.poblacion_total AS DOUBLE)) AS pob_total
        FROM read_csv('data/procesado/analisis_variables_base.csv') a
        JOIN read_csv('data/procesado/eustat_demografia_renta_252.csv') b
          ON a.codigo_ine = b.codigo_ine
        GROUP BY a.territorio
    """).df()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=df, x="territorio", y="pob_total", ax=axes[0], palette="Greens")
    axes[0].set_title("E: Poblacion total media por territorio")
    axes[0].set_ylabel("Habitantes")
    axes[0].set_xlabel("")
    axes[1].axis("off")
    axes[1].text(0.5, 0.5, "No disponible en fuente Eustat (solo grupos 0-19, 20-64, >=65)",
                 ha="center", va="center", fontsize=11, wrap=True)
    axes[1].set_title("E: Poblacion joven 15-29 media")
    return _save(fig, "E_demografia.png")


def g_F_comparativa_th():
    df = duckdb.query("""
        SELECT territorio,
               AVG(renta_media_eur_m2_media) AS precio_medio,
               AVG(tasa_paro_lanbide_pct) AS paro_medio,
               AVG(renta_personal_total_eur) AS renta_media
        FROM read_csv('data/procesado/analisis_variables_base.csv')
        GROUP BY territorio
    """).df()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    sns.barplot(data=df, x="territorio", y="precio_medio", ax=axes[0], palette="Blues")
    axes[0].set_title("F4: Precio alquiler medio (EUR/m2)")
    axes[0].set_ylabel("EUR/m2")
    axes[0].set_xlabel("")
    sns.barplot(data=df, x="territorio", y="paro_medio", ax=axes[1], palette="Reds")
    axes[1].set_title("F4: Paro juvenil medio (%)")
    axes[1].set_ylabel("%")
    axes[1].set_xlabel("")
    sns.barplot(data=df, x="territorio", y="renta_media", ax=axes[2], palette="Greens")
    axes[2].set_title("F4: Renta personal total media (EUR)")
    axes[2].set_ylabel("EUR")
    axes[2].set_xlabel("")
    return _save(fig, "F_comparativa_th.png")


def g_G_gaps():
    gaps = [
        ("93 municipios sin alquiler oficial", "imputados por comarca"),
        ("170 municipios sin anuncios", "solo 6 robustos (n>=30)"),
        ("VPO Etxebide", "83.73% ceros, sin stock real"),
        ("ECVI compraventa", "solo 7 municipios >40k"),
        ("Emancipacion juvenil", "solo nivel CAE, no municipal"),
        ("Pisos sin geo", "235/235 sin coordenadas"),
        ("Duplicados anuncios", "13.45% sin fingerprint"),
        ("Transporte paradas", "252 nulos en paradas_por_1000_hab"),
        ("Cert. energetico", "467/470 en Fotocasa detalle"),
        ("Mezcla de anos", "anuncios 2026 vs alquiler/renta 2024"),
    ]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")
    table = ax.table(cellText=gaps, colLabels=["Gap / Limitacion", "Detalle"],
                     loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    ax.set_title("G: Limitaciones y gaps documentados (O4)", fontsize=14, pad=20)
    return _save(fig, "G_gaps_limitaciones.png")


def main():
    print("Generando dashboard completo (7 bloques)...")
    g_A1_esfuerzo_territorio()
    g_A2_municipios_inasequibles()
    g_B_paro_vs_precio()
    g_C_vpo_antiguedad()
    g_D_distancia_precio()
    g_E_demografia()
    g_F_comparativa_th()
    g_G_gaps()
    print(f"\n8 graficos guardados en {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
