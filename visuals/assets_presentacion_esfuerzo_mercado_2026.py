"""Genera assets de esfuerzo de mercado 2026 para la presentacion v2.

Estilo Swiss Modern (misma paleta que docs/presentacion_v2/index.html):
  papel #F5F4F0, tinta #121212, muted #6E6B66, acento #C8451B.

Lee data/procesado/esfuerzo_mercado_2026.csv y escribe PNG transparente en
docs/presentacion_v2/assets/ para que compaginen con las diapositivas existentes.

No toca raw ni esfuerzo canonico 2024. Capa paralela.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "procesado"
ASSETS = ROOT / "docs" / "presentacion_v2" / "assets"

PAPER = "#F5F4F0"
INK = "#121212"
MUTED = "#6E6B66"
ACCENT = "#C8451B"

SRC = PROC / "esfuerzo_mercado_2026.csv"


def _cargar() -> pd.DataFrame:
    if not SRC.exists():
        raise SystemExit(f"Falta {SRC}. Ejecuta calcular_esfuerzo_mercado_2026.py")
    df = pd.read_csv(SRC, encoding="utf-8-sig", dtype=str)
    df["esf_18_34"] = pd.to_numeric(df["esfuerzo_mercado_2026_pct_18_34"], errors="coerce")
    df["precio_med"] = pd.to_numeric(df["precio_mediana_anuncio_2026_eur_mes"], errors="coerce")
    df["n_anun"] = pd.to_numeric(df["n_anuncios_2026"], errors="coerce")
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
    """Top 20 municipios por esfuerzo mercado 2026 (pct 18-34)."""
    d = df.dropna(subset=["esf_18_34"]).copy()
    d = d.sort_values("esf_18_34", ascending=True).tail(20)
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    colores = [ACCENT if v >= 100 else "#9A5A2E" for v in d["esf_18_34"]]
    bars = ax.barh(d["nombre_canonico"], d["esf_18_34"], color=colores, height=0.62)
    for b, v in zip(bars, d["esf_18_34"]):
        ax.text(v + 1.5, b.get_y() + b.get_height() / 2, f"{v:.1f} %",
                va="center", ha="left", fontsize=9.5, color=INK)
    ax.axvline(100, color=ACCENT, linewidth=1.6, linestyle="--")
    ax.text(100, len(d) - 0.4, "  100 % (salario entero)", color=ACCENT,
            fontsize=9, va="bottom", ha="left", fontweight="bold")
    ax.set_xlabel("Esfuerzo de mercado 2026 (% salario joven 18-34)", color=INK, fontsize=11)
    ax.set_title("Top 20 municipios — precio de anuncio 2026 vs salario joven 2024 (IPC INE)",
                 color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.set_xlim(0, d["esf_18_34"].max() * 1.28)
    _guardar(fig, "M26_top20_esfuerzo_mercado.png")


def grafico_histograma(df: pd.DataFrame) -> None:
    """Histograma del esfuerzo mercado 2026."""
    d = df.dropna(subset=["esf_18_34"])
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bins = [0, 25, 50, 75, 100, 125, 150, 200, 300, 500]
    ax.hist(d["esf_18_34"], bins=bins, color=ACCENT, alpha=0.9, edgecolor="white", linewidth=0.8)
    mediana = d["esf_18_34"].median()
    ax.axvline(mediana, color=INK, linewidth=2)
    ax.text(mediana + 3, ax.get_ylim()[1] * 0.92, f"mediana {mediana:.1f} %",
            color=INK, fontsize=10, fontweight="bold", va="top")
    ax.axvline(30, color="#9A5A2E", linewidth=1.6, linestyle="--")
    ax.text(30, ax.get_ylim()[1] * 0.78, "umbral 30 %", color="#9A5A2E",
            fontsize=9, va="top", ha="right", fontweight="bold")
    ax.set_xlabel("Esfuerzo de mercado 2026 (% salario joven 18-34)", color=INK, fontsize=11)
    ax.set_ylabel("Municipios", color=INK, fontsize=11)
    ax.set_title("Distribucion del esfuerzo de mercado 2026 (52 municipios con anuncio)",
                 color=INK, fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    _guardar(fig, "M26_hist_esfuerzo_mercado.png")


def grafico_territorio(df: pd.DataFrame) -> None:
    """Esfuerzo mediano por territorio."""
    d = df.dropna(subset=["esf_18_34", "territorio"])
    agg = d.groupby("territorio")["esf_18_34"].median().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    bars = ax.bar(agg["territorio"], agg["esf_18_34"], color=ACCENT, width=0.55)
    for b, v in zip(bars, agg["esf_18_34"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f} %",
                ha="center", va="bottom", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_ylabel("Esfuerzo mediano 2026 (% salario 18-34)", color=INK, fontsize=11)
    ax.set_title("Esfuerzo de mercado 2026 por territorio (mediana)", color=INK,
                 fontsize=12, loc="left", pad=12)
    _estilo_ax(ax)
    ax.grid(axis="x", color="#CFCBC3", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_ylim(0, agg["esf_18_34"].max() * 1.22)
    _guardar(fig, "M26_esfuerzo_por_territorio.png")


def main() -> int:
    df = _cargar()
    con_dato = df.dropna(subset=["esf_18_34"])
    print(f"Leido {SRC.name}: {len(df)} municipios, {len(con_dato)} con esfuerzo")
    print(f"Mediana esfuerzo 18-34: {con_dato['esf_18_34'].median():.1f} %")
    print(f"Mediana precio anuncio: {con_dato['precio_med'].median():.0f} €/mes")
    grafico_barras_top20(df)
    grafico_histograma(df)
    grafico_territorio(df)
    print(f"Assets escritos en {ASSETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
