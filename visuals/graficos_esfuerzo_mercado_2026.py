"""Genera visualizaciones del esfuerzo de mercado 2026.

Lee data/procesado/esfuerzo_mercado_2026.csv y escribe PNG en
visuals/esfuerzo_mercado_2026/:

  1. barras_esfuerzo_top20.png   — top 20 municipios por esfuerzo (pct 18-34)
  2. hist_esfuerzo.png           — histograma del esfuerzo (pct 18-34)
  3. barras_territorio.png       — esfuerzo mediano por territorio
  4. scatter_precio_vs_esfuerzo.png — precio mediano anuncio vs esfuerzo

No toca raw ni esfuerzo canonico 2024. Solo lectura del silver generado.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"Falta dependencia de visualizacion: {exc}")

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "procesado"
OUT = ROOT / "visuals" / "esfuerzo_mercado_2026"

SRC = PROC / "esfuerzo_mercado_2026.csv"

sns.set_style("whitegrid")
plt.rcParams["figure.autolayout"] = True


def _cargar() -> pd.DataFrame:
    if not SRC.exists():
        raise SystemExit(f"Falta {SRC}. Ejecuta primero calcular_esfuerzo_mercado_2026.py")
    df = pd.read_csv(SRC, encoding="utf-8-sig", dtype=str)
    df["esfuerzo_mercado_2026_pct_18_34"] = pd.to_numeric(
        df["esfuerzo_mercado_2026_pct_18_34"], errors="coerce"
    )
    df["precio_mediana_anuncio_2026_eur_mes"] = pd.to_numeric(
        df["precio_mediana_anuncio_2026_eur_mes"], errors="coerce"
    )
    df["n_anuncios_2026"] = pd.to_numeric(df["n_anuncios_2026"], errors="coerce")
    return df


def _guardar(fig, nombre: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ruta = OUT / nombre
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {ruta}")


def grafico_barras_top20(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esfuerzo_mercado_2026_pct_18_34"]).copy()
    d = d.sort_values("esfuerzo_mercado_2026_pct_18_34", ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(
        d["nombre_canonico"],
        d["esfuerzo_mercado_2026_pct_18_34"],
        color=sns.color_palette("rocket", n_colors=len(d)),
    )
    ax.invert_yaxis()
    ax.set_xlabel("Esfuerzo mercado 2026 (% salario joven 18-34)")
    ax.set_title("Top 20 municipios — esfuerzo de alquiler 2026 (pct 18-34)")
    for i, v in enumerate(d["esfuerzo_mercado_2026_pct_18_34"]):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center")
    _guardar(fig, "barras_esfuerzo_top20.png")


def grafico_histograma(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esfuerzo_mercado_2026_pct_18_34"])
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(d["esfuerzo_mercado_2026_pct_18_34"], bins=12, edgecolor="white", color="#4c72b0")
    ax.set_xlabel("Esfuerzo mercado 2026 (% salario joven 18-34)")
    ax.set_ylabel("N municipios")
    ax.set_title("Distribucion del esfuerzo de mercado 2026 (municipios con anuncio)")
    _guardar(fig, "hist_esfuerzo.png")


def grafico_territorio(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esfuerzo_mercado_2026_pct_18_34", "territorio"])
    agg = (
        d.groupby("territorio")["esfuerzo_mercado_2026_pct_18_34"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(agg["territorio"], agg["esfuerzo_mercado_2026_pct_18_34"], color="#55a868")
    ax.set_ylabel("Esfuerzo mediano 2026 (% salario 18-34)")
    ax.set_title("Esfuerzo de mercado 2026 por territorio (mediana)")
    for i, v in enumerate(agg["esfuerzo_mercado_2026_pct_18_34"]):
        ax.text(i, v + 0.5, f"{v:.1f}", ha="center")
    _guardar(fig, "barras_territorio.png")


def grafico_scatter(df: pd.DataFrame) -> None:
    d = df.dropna(
        subset=["esfuerzo_mercado_2026_pct_18_34", "precio_mediana_anuncio_2026_eur_mes"]
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        d["precio_mediana_anuncio_2026_eur_mes"],
        d["esfuerzo_mercado_2026_pct_18_34"],
        s=40,
        alpha=0.7,
        color="#dd8452",
        edgecolor="white",
    )
    ax.set_xlabel("Precio mediana anuncio 2026 (€/mes)")
    ax.set_ylabel("Esfuerzo mercado 2026 (% salario 18-34)")
    ax.set_title("Precio de alquiler vs esfuerzo de mercado 2026")
    _guardar(fig, "scatter_precio_vs_esfuerzo.png")


def main() -> int:
    df = _cargar()
    print(f"Leído {SRC.name}: {len(df)} municipios")
    grafico_barras_top20(df)
    grafico_histograma(df)
    grafico_territorio(df)
    grafico_scatter(df)
    print(f"Imagenes escritas en {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
