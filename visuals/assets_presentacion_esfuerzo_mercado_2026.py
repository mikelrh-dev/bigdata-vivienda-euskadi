"""Genera assets de esfuerzo de mercado 2026 para la presentacion v2.

Estilo Swiss Modern (misma paleta que docs/presentacion_v2/index.html):
  papel #F5F4F0, tinta #121212, muted #6E6B66, acento #C8451B.

Lee los CSV de `data/procesado` (no teclea cifras) y escribe PNG transparente en
docs/presentacion_v2/assets/ para que compaginen con las diapositivas.

Assets:
  - M26_top20_esfuerzo_mercado.png   top con n>=5 y IC95 %
  - M26_hist_esfuerzo_mercado.png    distribucion municipal
  - M26_esfuerzo_por_territorio.png  mediana por territorio
  - M26_esfuerzo_por_tipo.png        ponderado por anuncios, por tipologia
  - M26_brecha_2024_2026.png         diferencia de nivel por municipio
  - M26_ic_esfuerzo.png              intervalos de confianza (n>=5)
  - M26_cobertura.png                cobertura por poblacion 18-34 y territorio
  - M26_mapa_coropletico_2026.png    copia del mapa de esfuerzo
  - M26_mapa_cobertura.png           copia del mapa de n

No toca raw ni esfuerzo canonico 2024. Capa paralela.

Uso:
    python visuals/assets_presentacion_esfuerzo_mercado_2026.py
"""

from __future__ import annotations

import shutil
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "procesado"
ASSETS = ROOT / "docs" / "presentacion_v2" / "assets"
FIGURAS = ROOT / "visuals" / "esfuerzo_mercado_2026"

PAPER = "#F5F4F0"
INK = "#121212"
MUTED = "#6E6B66"
ACCENT = "#C8451B"
SECOND = "#9A5A2E"
GRIS = "#C9C5BD"

SRC = PROC / "esfuerzo_mercado_2026.csv"
SRC_TIPO = PROC / "esfuerzo_mercado_2026_por_tipo.csv"
SRC_TIPO_ANUNCIO = ROOT / "data" / "resultados" / "esfuerzo_por_tipo_nivel_anuncio_2026.csv"
SRC_BRECHA = ROOT / "data" / "resultados" / "brecha_esfuerzo_2024_2026.csv"
SRC_COB = ROOT / "data" / "resultados" / "cobertura_representatividad_2026.csv"


def _cargar() -> pd.DataFrame:
    if not SRC.exists():
        raise SystemExit(f"Falta {SRC}. Ejecuta calcular_esfuerzo_mercado_2026.py")
    df = pd.read_csv(SRC, encoding="utf-8-sig", dtype=str)
    for col in ("esfuerzo_mercado_2026_pct_18_34", "precio_mediana_anuncio_2026_eur_mes",
                "n_anuncios_2026", "ic95_lo_pct_18_34", "ic95_hi_pct_18_34"):
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    df["esf_18_34"] = df["esfuerzo_mercado_2026_pct_18_34"]
    df["precio_med"] = df["precio_mediana_anuncio_2026_eur_mes"]
    df["n_anun"] = df["n_anuncios_2026"]
    return df


def _estilo_ax(ax) -> None:
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color="#CFCBC3", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelsize=10)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(MUTED)


def _guardar(fig, nombre: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    ruta = ASSETS / nombre
    fig.savefig(ruta, dpi=150, bbox_inches="tight", transparent=True, facecolor="none")
    plt.close(fig)
    print(f"OK: {ruta}")


def grafico_barras_top20(df: pd.DataFrame) -> None:
    """Top por esfuerzo entre municipios con n>=5, con IC95 %."""
    d = df.dropna(subset=["esf_18_34"])
    d = d[d["n_anun"] >= 5].sort_values("esf_18_34", ascending=True).tail(20)
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    colores = [ACCENT if v >= 100 else SECOND for v in d["esf_18_34"]]
    bars = ax.barh(d["nombre_canonico"], d["esf_18_34"], color=colores, height=0.62)
    lo = (d["esf_18_34"] - d["ic95_lo_pct_18_34"]).fillna(0).clip(lower=0)
    hi = (d["ic95_hi_pct_18_34"] - d["esf_18_34"]).fillna(0).clip(lower=0)
    ax.errorbar(d["esf_18_34"], range(len(d)), xerr=[lo, hi], fmt="none",
                ecolor=INK, capsize=3, elinewidth=1.1)
    for b, v, n in zip(bars, d["esf_18_34"], d["n_anun"]):
        ax.text(v + 2, b.get_y() + b.get_height() / 2, f"{v:.0f} % (n={int(n)})",
                va="center", ha="left", fontsize=9, color=INK)
    ax.axvline(30, color=SECOND, linewidth=1.4, linestyle="--")
    ax.text(30, -0.8, " umbral 30 %", color=SECOND, fontsize=8.5, va="bottom", ha="left")
    ax.set_xlabel("Esfuerzo de mercado 2026 (% salario joven 18-34), IC95 % bootstrap",
                  color=INK, fontsize=10.5)
    ax.set_title(f"Municipios con n>=5 — anuncio 2026 vs salario joven (IPC INE)",
                 color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.set_xlim(0, max(d["esf_18_34"].max(), d["ic95_hi_pct_18_34"].max()) * 1.25)
    _guardar(fig, "M26_top20_esfuerzo_mercado.png")


def _p1(x: float) -> str:
    """Un decimal con redondeo mitad-arriba (78,55 -> 78.6), como el resto del proyecto."""
    return str(Decimal(repr(round(float(x), 6))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def grafico_histograma(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esf_18_34"])
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bins = [0, 25, 50, 75, 100, 125, 150, 200, 300, 500]
    ax.hist(d["esf_18_34"], bins=bins, color=ACCENT, alpha=0.9,
            edgecolor="white", linewidth=0.8)
    mediana = d["esf_18_34"].median()
    ax.axvline(mediana, color=INK, linewidth=2)
    ax.text(mediana + 3, ax.get_ylim()[1] * 0.92, f"mediana {_p1(mediana)} %",
            color=INK, fontsize=10, fontweight="bold", va="top")
    ax.axvline(30, color=SECOND, linewidth=1.6, linestyle="--")
    ax.text(30, ax.get_ylim()[1] * 0.78, "umbral 30 %", color=SECOND,
            fontsize=9, va="top", ha="right", fontweight="bold")
    ax.set_xlabel("Esfuerzo de mercado 2026 (% salario joven 18-34)", color=INK, fontsize=11)
    ax.set_ylabel("Municipios", color=INK, fontsize=11)
    ax.set_title(f"Distribucion del esfuerzo de mercado 2026 ({len(d)} municipios con anuncio)",
                 color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    _guardar(fig, "M26_hist_esfuerzo_mercado.png")


def grafico_territorio(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esf_18_34", "territorio"])
    agg = d.groupby("territorio")["esf_18_34"].median().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    bars = ax.bar(agg["territorio"], agg["esf_18_34"], color=ACCENT, width=0.55)
    for b, v in zip(bars, agg["esf_18_34"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{_p1(v)} %",
                ha="center", va="bottom", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_ylabel("Esfuerzo mediano 2026 (% salario 18-34)", color=INK, fontsize=11)
    ax.set_title("Esfuerzo de mercado 2026 por territorio (mediana)", color=INK,
                 fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.grid(axis="x", color="#CFCBC3", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_ylim(0, agg["esf_18_34"].max() * 1.22)
    _guardar(fig, "M26_esfuerzo_por_territorio.png")


def grafico_por_tipo() -> None:
    """Mediana a nivel de anuncio (estimador directo) con IC95 %.

    Si falta el CSV de analisis, cae al ponderado municipal y lo dice en el
    titulo: nunca se rotula como directo lo que es una media de medianas.
    """
    if SRC_TIPO_ANUNCIO.exists():
        df = pd.read_csv(SRC_TIPO_ANUNCIO, encoding="utf-8-sig")
        cols = ("esfuerzo_mediana_anuncios_pct_18_34", "ic95_lo_pct_18_34",
                "ic95_hi_pct_18_34", "n_anuncios")
        for col in cols:
            df[col] = pd.to_numeric(df.get(col), errors="coerce")
        df = df.dropna(subset=["esfuerzo_mediana_anuncios_pct_18_34", "n_anuncios"])
        df = df.sort_values("tipo_de_vivienda")
        etiquetas = df["tipo_de_vivienda"].tolist()
        valores = df["esfuerzo_mediana_anuncios_pct_18_34"].tolist()
        ns = df["n_anuncios"].tolist()
        lo = df["ic95_lo_pct_18_34"].tolist()
        hi = df["ic95_hi_pct_18_34"].tolist()
        titulo = "Esfuerzo por tipologia: mediana de los anuncios (IC95 %)"
    elif SRC_TIPO.exists():
        df = pd.read_csv(SRC_TIPO, encoding="utf-8-sig", dtype=str)
        for col in ("precio_mediana_eur", "n_anuncios", "esfuerzo_mercado_2026_pct_18_34"):
            df[col] = pd.to_numeric(df.get(col), errors="coerce")
        df = df.dropna(subset=["esfuerzo_mercado_2026_pct_18_34", "n_anuncios"])
        agg = (df.assign(peso=df["n_anuncios"])
                 .groupby("tipo_de_vivienda")
                 .apply(lambda g: (g["esfuerzo_mercado_2026_pct_18_34"] * g["peso"]).sum()
                        / g["peso"].sum(), include_groups=False)
                 .reset_index(name="esfuerzo"))
        n_por_tipo = df.groupby("tipo_de_vivienda")["n_anuncios"].sum()
        etiquetas = agg["tipo_de_vivienda"].tolist()
        valores = agg["esfuerzo"].tolist()
        ns = [int(n_por_tipo[t]) for t in etiquetas]
        lo = hi = None
        titulo = "Esfuerzo por tipologia (media de medianas municipales)"
    else:
        print(f"AVISO: falta {SRC_TIPO.name}; se omite el grafico por tipo")
        return

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    bars = ax.bar(etiquetas, valores, color=ACCENT, width=0.5)
    if lo is not None:
        ax.errorbar(range(len(valores)), valores,
                    yerr=[[v - l for v, l in zip(valores, lo)],
                          [h - v for v, h in zip(valores, hi)]],
                    fmt="none", ecolor=INK, elinewidth=1.2, capsize=5)
    techos = hi if hi is not None else valores
    for b, v, n, t in zip(bars, valores, ns, techos):
        ax.text(b.get_x() + b.get_width() / 2, max(v, t) + max(valores) * 0.03,
                f"{_p1(v)} %\n(n={n})", ha="center", va="bottom",
                fontsize=9.5, color=INK)
    ax.axhline(30, color=SECOND, linestyle="--", linewidth=1.3)
    ax.set_ylabel("Esfuerzo 2026 (% salario 18-34)", color=INK, fontsize=11)
    ax.set_title(titulo, color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(valores) * 1.32)
    _guardar(fig, "M26_esfuerzo_por_tipo.png")


def grafico_brecha() -> None:
    if not SRC_BRECHA.exists():
        print(f"AVISO: falta {SRC_BRECHA.name}; se omite el grafico de brecha")
        return
    df = pd.read_csv(SRC_BRECHA, encoding="utf-8-sig", dtype=str)
    for col in ("brecha_pp_18_34", "esfuerzo_2024_pct_18_34",
                "esfuerzo_2026_pct_18_34", "n_anuncios_2026"):
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    df = df.dropna(subset=["brecha_pp_18_34"])
    d = df.sort_values("brecha_pp_18_34", ascending=True).tail(15).copy()
    # Solo las barras con muestra suficiente van en color: el resto es ruido
    # de n=1 y no puede leerse como tendencia.
    d["suficiente"] = d["n_anuncios_2026"] >= 5
    colores = [SECOND if ok else GRIS for ok in d["suficiente"]]
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    bars = ax.barh(d["nombre_canonico"], d["brecha_pp_18_34"], color=colores, height=0.62)
    for b, v, n in zip(bars, d["brecha_pp_18_34"], d["n_anuncios_2026"]):
        ax.text(v + 1, b.get_y() + b.get_height() / 2, f"{v:+.1f} pp (n={int(n)})",
                va="center", ha="left", fontsize=9, color=INK)
    ax.axvline(0, color=INK, linewidth=1.2)
    ax.text(0.985, 0.03, "gris = n<5 (no concluyente)", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Diferencia de nivel 2026 oferta - 2024 registrado (pp)", color=INK, fontsize=10.5)
    ax.set_title("Diferencia de NIVEL, no variacion temporal: cambia numerador y denominador",
                 color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.set_xlim(0, d["brecha_pp_18_34"].max() * 1.38)
    _guardar(fig, "M26_brecha_2024_2026.png")


def grafico_ic(df: pd.DataFrame) -> None:
    """Dot plot con IC95 % para los municipios con n>=5."""
    d = df.dropna(subset=["esf_18_34", "ic95_lo_pct_18_34", "ic95_hi_pct_18_34"])
    d = d[d["n_anun"] >= 5].sort_values("esf_18_34")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    y = range(len(d))
    ax.hlines(list(y), d["ic95_lo_pct_18_34"], d["ic95_hi_pct_18_34"],
              color=SECOND, linewidth=2)
    ax.plot(d["esf_18_34"], list(y), "o", color=ACCENT, markersize=7)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{n} (n={int(k)})" for n, k in zip(d["nombre_canonico"], d["n_anun"])])
    ax.axvline(30, color=MUTED, linestyle="--", linewidth=1.3)
    ax.set_xlabel("Esfuerzo 2026 (% salario joven 18-34), IC95 % bootstrap", color=INK, fontsize=10.5)
    ax.set_title("Intervalos de confianza: lo que sostiene cada municipio", color=INK,
                 fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#CFCBC3", linewidth=0.8)
    _guardar(fig, "M26_ic_esfuerzo.png")


def grafico_cobertura() -> None:
    if not SRC_COB.exists():
        print(f"AVISO: falta {SRC_COB.name}; se omite el grafico de cobertura")
        return
    df = pd.read_csv(SRC_COB, encoding="utf-8-sig", dtype=str)
    terr = df[df["metrica"].str.startswith("pct_poblacion_18_34_cubierta_")].copy()
    total = df[df["metrica"] == "pct_poblacion_18_34_cubierta"].iloc[0]
    terr["etiqueta"] = terr["metrica"].str.replace(
        "pct_poblacion_18_34_cubierta_", "", regex=False)
    terr["valor"] = pd.to_numeric(terr["valor"], errors="coerce")
    terr = terr.dropna(subset=["valor"]).sort_values("valor", ascending=True)
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    bars = ax.barh(terr["etiqueta"], terr["valor"], color=ACCENT, height=0.55)
    for b, v in zip(bars, terr["valor"]):
        ax.text(v + 1, b.get_y() + b.get_height() / 2, f"{_p1(v)} %",
                va="center", ha="left", fontsize=10, color=INK)
    total_pct = float(total["valor"])
    ax.axvline(total_pct, color=INK, linestyle="--", linewidth=1.3)
    ax.text(total_pct - 1, -0.55,
            f"total {_p1(total_pct)} %", color=INK, fontsize=9,
            ha="right", va="bottom")
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de poblacion 18-34 en municipios con anuncio", color=INK, fontsize=10.5)
    ax.set_title("Cobertura de la capa 2026: poblacion, no municipios", color=INK,
                 fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#CFCBC3", linewidth=0.8)
    _guardar(fig, "M26_cobertura.png")


def copiar_mapas() -> None:
    pares = {
        FIGURAS / "mapa_coropletico_2026.png": "M26_mapa_coropletico_2026.png",
        FIGURAS / "mapa_cobertura_2026.png": "M26_mapa_cobertura.png",
    }
    for origen, destino in pares.items():
        if not origen.exists():
            print(f"AVISO: falta {origen.name}; ejecuta visuals/mapa_esfuerzo_mercado_2026.py")
            continue
        ASSETS.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origen, ASSETS / destino)
        print(f"OK: {ASSETS / destino}")


def main() -> int:
    df = _cargar()
    con_dato = df.dropna(subset=["esf_18_34"])
    print(f"Leido {SRC.name}: {len(df)} municipios, {len(con_dato)} con esfuerzo, "
          f"{int(con_dato['n_anun'].sum())} anuncios")
    print(f"Mediana esfuerzo 18-34: {con_dato['esf_18_34'].median():.2f} %")
    print(f"Mediana precio anuncio: {con_dato['precio_med'].median():.0f} EUR/mes")
    grafico_barras_top20(df)
    grafico_histograma(df)
    grafico_territorio(df)
    grafico_por_tipo()
    grafico_brecha()
    grafico_ic(df)
    grafico_cobertura()
    copiar_mapas()
    print(f"Assets escritos en {ASSETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
