"""Genera mapa coropletico del esfuerzo de mercado 2026 por municipio.

Lee:
  - data/procesado/municipios_euskadi_252.geojson (features en datos.features,
    properties.codigo_ine)
  - data/procesado/esfuerzo_mercado_2026.csv (esfuerzo_mercado_2026_pct_18_34)

Genera un choropleth con matplotlib puro (sin geopandas): parches de poligono
por municipio, coloreados por esfuerzo. Municipios sin datos en gris claro.

NO toca raw ni esfuerzo canonico 2024.

Guarda:
    visuals/esfuerzo_mercado_2026/mapa_coropletico_2026.png

Uso:
    python visuals/mapa_esfuerzo_mercado_2026.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon, Patch
    from matplotlib.colors import Normalize
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"Falta dependencia de visualizacion: {exc}")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"
OUT_DIR = PROJECT_ROOT / "visuals" / "esfuerzo_mercado_2026"

GEOJSON = PROC / "municipios_euskadi_252.geojson"
MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
OUT = OUT_DIR / "mapa_coropletico_2026.png"
OUT_COBERTURA = OUT_DIR / "mapa_cobertura_2026.png"
N_MIN_FIABLE = 5

COLOR_SIN_DATOS = "#d3d3d3"
CMAP = "YlOrRd"


def _anillos_geometria(geom: dict) -> list:
    """Devuelve las listas de anillos (exteriores) de una geometria."""
    tipo = geom.get("type")
    coords = geom.get("coordinates")
    anillos: list = []
    if tipo == "Polygon":
        anillos = list(coords)
    elif tipo == "MultiPolygon":
        for poligono in coords:
            anillos.extend(poligono)
    return anillos


def main() -> int:
    if not GEOJSON.exists():
        print(f"Falta {GEOJSON.name}.")
        return 1
    if not MERCADO_2026.exists():
        print(f"Falta {MERCADO_2026.name}. Ejecuta primero calcular_esfuerzo_mercado_2026.py")
        return 1

    with GEOJSON.open(encoding="utf-8-sig") as f:
        geo = json.load(f)
    features = geo["datos"]["features"]

    df = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)
    df["esfuerzo_mercado_2026_pct_18_34"] = pd.to_numeric(
        df["esfuerzo_mercado_2026_pct_18_34"], errors="coerce"
    )
    df["n_anuncios_2026"] = pd.to_numeric(df["n_anuncios_2026"], errors="coerce")
    esfuerzo = df.set_index("codigo_ine")["esfuerzo_mercado_2026_pct_18_34"]
    anuncios = df.set_index("codigo_ine")["n_anuncios_2026"]
    n_insuficiente = set(df.loc[df["n_anuncios_2026"] < N_MIN_FIABLE, "codigo_ine"])

    valores = esfuerzo.dropna()
    if valores.empty:
        print("No hay valores de esfuerzo para dibujar el mapa.")
        return 1
    vmin, vmax = float(valores.min()), float(valores.max())

    cmap = plt.get_cmap(CMAP)
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax.axis("off")

    n_con_dato = 0
    n_sin_dato = 0
    for feat in features:
        props = feat.get("properties", {})
        code = str(props.get("codigo_ine", "")).zfill(5)
        valor = esfuerzo.get(code, float("nan"))
        anillos = _anillos_geometria(feat.get("geometry", {}))
        if pd.isna(valor):
            facecolor = COLOR_SIN_DATOS
            hatch = None
            n_sin_dato += 1
        else:
            facecolor = cmap(norm(float(valor)))
            # n<5 no sostiene una mediana municipal: se marca con trama.
            hatch = "///" if code in n_insuficiente else None
            n_con_dato += 1
        for anillo in anillos:
            polygon = MplPolygon(
                anillo, closed=True,
                facecolor=facecolor, edgecolor="white", linewidth=0.3,
                antialiased=True, hatch=hatch,
            )
            ax.add_patch(polygon)

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Esfuerzo mercado 2026 (% salario joven 18-34)")

    ax.set_title(
        "Esfuerzo de mercado de alquiler 2026 por municipio\n"
        "(pct del salario joven 18-34, ajuste IPC INE 2024->2026)",
        fontsize=12,
        pad=12,
    )

    leyenda = [
        Patch(facecolor=COLOR_SIN_DATOS, edgecolor="white", label="Sin datos"),
        Patch(facecolor="#f0b27a", edgecolor="white", hatch="///",
              label=f"n<{N_MIN_FIABLE}: no concluyente"),
    ]
    ax.legend(handles=leyenda, loc="lower left", frameon=True, fontsize=9)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(
        f"OK: {OUT.name} ({n_con_dato} municipios con dato, "
        f"{n_sin_dato} sin dato, vmin={vmin:.2f}, vmax={vmax:.2f})"
    )

    # Segundo mapa: cobertura (n de anuncios), para no confundir gris con barato.
    valores_n = anuncios.dropna()
    valores_n = valores_n[valores_n > 0]
    norm_n = Normalize(vmin=1, vmax=float(valores_n.max()))
    cmap_n = plt.get_cmap("Blues")
    fig2, ax2 = plt.subplots(figsize=(10, 10))
    ax2.set_aspect("equal")
    ax2.axis("off")
    for feat in features:
        props = feat.get("properties", {})
        code = str(props.get("codigo_ine", "")).zfill(5)
        n = anuncios.get(code, float("nan"))
        facecolor = COLOR_SIN_DATOS if (pd.isna(n) or n == 0) else cmap_n(norm_n(float(n)))
        for anillo in _anillos_geometria(feat.get("geometry", {})):
            ax2.add_patch(MplPolygon(
                anillo, closed=True, facecolor=facecolor,
                edgecolor="white", linewidth=0.3, antialiased=True,
            ))
    sm2 = plt.cm.ScalarMappable(norm=norm_n, cmap=cmap_n)
    sm2.set_array([])
    cbar2 = fig2.colorbar(sm2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label("Anuncios 2026 usados (n)")
    ax2.set_title(
        "Cobertura de la capa 2026: anuncios por municipio\n"
        "(gris = sin anuncio: 'sin dato', no 'asequible')",
        fontsize=12, pad=12,
    )
    fig2.savefig(OUT_COBERTURA, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"OK: {OUT_COBERTURA.name} ({len(valores_n)} municipios con anuncio)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
