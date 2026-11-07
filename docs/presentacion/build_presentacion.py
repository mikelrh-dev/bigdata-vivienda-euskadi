"""Genera la presentacion de defensa (HTML + SVG) desde los CSV del proyecto.

Uso:
    .venv/Scripts/python.exe docs/presentacion/build_presentacion.py
    # PDF: ver README.md (Chrome headless)
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "data" / "resultados"
OUT = Path(__file__).resolve().parent
ASSETS = OUT / "assets"
ASSETS.mkdir(exist_ok=True)

# Paleta de tinta sobre papel (las diapositivas 1-7 y 10 son claras).
NAVY = "#12233A"
INK = "#2A3B4D"
MUTED = "#8C8577"
ACCENT = "#A8481F"
TEAL = "#1F4B43"
RED = "#8C2B1E"
GRID = "#D8D1C2"
PAPER = "#F4F0E6"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "svg.fonttype": "none",
})


def _es(v: float, dec: int = 2) -> str:
    return f"{v:.{dec}f}".replace(".", ",")


def _clean(ax) -> None:
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def chart_histograma(esf: pd.Series, mediana: float, n30: int, total: int) -> Path:
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    bins = np.arange(10, 50, 2.5)
    ax.hist(esf, bins=bins, color=ACCENT, alpha=0.88, edgecolor=PAPER, linewidth=0.9)
    ax.axvline(30, color=RED, linewidth=2, linestyle="--")
    ax.axvline(mediana, color=NAVY, linewidth=2)
    placa = dict(facecolor=PAPER, edgecolor="none", pad=2.5, alpha=0.92)
    ax.text(29.3, ax.get_ylim()[1] * 0.95, "umbral 30 %", color=RED, fontsize=10, ha="right", bbox=placa)
    ax.text(mediana - 0.6, ax.get_ylim()[1] * 0.62, f"mediana {_es(mediana)} %",
            color=NAVY, fontsize=10, ha="right", bbox=placa)
    ax.set_xlabel("esfuerzo alquiler joven 18-34 (%)")
    ax.set_ylabel("municipios")
    ax.set_xlim(10, 50)
    _clean(ax)
    fig.tight_layout()
    ruta = ASSETS / "histograma_esfuerzo.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_territorios(medias: pd.Series, ns: pd.Series) -> Path:
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    nombres = [t.split("/")[0] for t in medias.index]
    etiquetas = [f"{n} (n={int(ns[t])})" for n, t in zip(nombres, medias.index)]
    ax.barh(etiquetas, medias.values, color=TEAL, height=0.55)
    for y, v in enumerate(medias.values):
        ax.text(v - 1.2, y, f"{_es(v)} %", va="center", ha="right", color=PAPER,
                fontsize=11, fontweight="bold")
    ax.axvline(30, color=RED, linewidth=2, linestyle="--")
    ax.set_xlim(0, 33)
    ax.set_xlabel("mediana del esfuerzo (%)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    ruta = ASSETS / "territorios.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_robustos(boot: pd.DataFrame, totales: dict[str, int]) -> Path:
    d = boot.sort_values("esfuerzo_canonico_pct")
    etiquetas = [
        f"{m} (n={totales.get(str(c), 0)})"
        for m, c in zip(d["municipio"], d["codigo_ine"])
    ]
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    y = np.arange(len(d))
    ax.barh(y, d["esfuerzo_canonico_pct"], color=ACCENT, alpha=0.45, edgecolor=ACCENT, height=0.55)
    ax.errorbar(
        d["esfuerzo_canonico_pct"], y,
        xerr=[d["esfuerzo_canonico_pct"] - d["ic95_inf"], d["ic95_sup"] - d["esfuerzo_canonico_pct"]],
        fmt="none", ecolor=NAVY, elinewidth=1.6, capsize=5,
    )
    for yi, v, sup in zip(y, d["esfuerzo_canonico_pct"], d["ic95_sup"]):
        ax.text(sup + 0.9, yi, f"{_es(v)} %", va="center", color=INK, fontsize=10, fontweight="bold")
    ax.set_yticks(y, etiquetas)
    ax.axvline(30, color=RED, linewidth=2, linestyle="--")
    ax.set_xlim(20, 52)
    ax.set_xlabel("esfuerzo canonico (%) e IC 95 % (bootstrap)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "robustos.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_tramos(tramos: dict[str, int], n_idw: int) -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 2.9))
    colores = [TEAL, ACCENT, RED]
    tinta = [PAPER, PAPER, PAPER]
    izquierda = 0
    for (nombre, valor), color, tcolor in zip(tramos.items(), colores, tinta):
        ax.barh(0, valor, left=izquierda, color=color, edgecolor=PAPER, height=0.55)
        ax.text(izquierda + valor / 2, 0, f"{valor}\n{nombre}", ha="center", va="center",
                color=tcolor, fontsize=10, fontweight="bold")
        izquierda += valor
    ax.barh(1, n_idw, color="#E7E0D0", edgecolor=MUTED, hatch="//", height=0.55)
    ax.text(n_idw / 2, 1, f"{n_idw}\nsolo estimacion", ha="center", va="center",
            color=INK, fontsize=10, fontweight="bold")
    ax.set_yticks([0, 1], [f"Dato oficial ({izquierda})", f"Sin cuantia oficial ({n_idw})"])
    ax.set_xlim(0, 160)
    ax.set_ylim(1.7, -0.7)
    ax.set_xlabel("municipios")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "tramos.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_sensibilidad(sens: pd.DataFrame) -> Path:
    d = sens.set_index("escenario")
    oficial, idw = d.loc["oficial_159"], d.loc["idw_252"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.1))
    for ax, col, titulo in ((ax1, "mediana_esfuerzo_pct", "mediana (%)"),
                            (ax2, "pct_sobre_30", "% de municipios > 30")):
        vals = [oficial[col], idw[col]]
        barras = ax.bar(["Oficial 159", "IDW 252"], vals, color=[TEAL, ACCENT],
                        edgecolor=[TEAL, ACCENT], width=0.55)
        for b, v in zip(barras, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.6, _es(v, 1) if col == "pct_sobre_30" else _es(v),
                    ha="center", color=INK, fontsize=10, fontweight="bold")
        ax.set_title(titulo, color=INK, fontsize=11, loc="left")
        ax.set_ylim(0, max(vals) * 1.35)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "sensibilidad.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


# --------------------------------------------------------------------------
# Imagenes decorativas (no son datos nuevos: son los mismos datos dibujados)
# --------------------------------------------------------------------------
def decor_topo() -> Path:
    """Curvas de nivel: Euskadi es monte; el relieve es contexto, no dato."""
    rng = np.random.default_rng(11)
    n = 420
    x = np.linspace(0, 10, n)
    y = np.linspace(0, 6, n)
    X, Y = np.meshgrid(x, y)

    Z = np.zeros_like(X)
    for _ in range(7):
        fx, fy = rng.uniform(0.5, 2.2, 2)
        ph = rng.uniform(0, 2 * np.pi)
        Z += rng.uniform(0.4, 1.0) * np.sin(fx * X + fy * Y + ph)
    Z += 0.45 * np.cos(3.1 * X - 1.3 * Y)

    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.contour(X, Y, Z, levels=24, colors=NAVY, linewidths=0.7, alpha=0.55)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    ruta = ASSETS / "topo.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def decor_trama(n_anuncios: int) -> Path:
    """Un pictograma de vivienda por anuncio: 594 dibujos, ni uno mas."""
    cols, rows, cell = 41, 20, 17
    w, h = 11, 10
    assert cols * rows >= n_anuncios, (cols * rows, n_anuncios)

    partes: list[str] = []
    i = 0
    for r in range(rows):
        for c in range(cols):
            if i >= n_anuncios:
                break
            cx, cy = 10 + c * cell, 10 + r * cell
            d = (
                f"M{cx} {cy + 4.2} L{cx + 5.5} {cy} L{cx + w} {cy + 4.2} "
                f"M{cx + 1.7} {cy + 3.4} L{cx + 1.7} {cy + h} "
                f"L{cx + 9.3} {cy + h} L{cx + 9.3} {cy + 3.4}"
            )
            partes.append(
                f'<path d="{d}" fill="none" stroke="{ACCENT}" '
                f'stroke-width="1.3" stroke-linecap="square"/>'
            )
            i += 1

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {10 + cols * cell} {10 + rows * cell}" '
        f'width="{10 + cols * cell}" height="{10 + rows * cell}">\n'
        f"<!-- {n_anuncios} anuncios: un pictograma por anuncio -->\n"
        + "\n".join(partes)
        + "\n</svg>\n"
    )
    ruta = ASSETS / "trama.svg"
    ruta.write_text(svg, encoding="utf-8")
    return ruta


# --------------------------------------------------------------------------
# Gráficos de incertidumbre de muestra (CONCLUSION-02): Tier B / mapa / burbuja
# --------------------------------------------------------------------------
def _num(v: object) -> float | None:
    """Convierte un escalar CSV a float o None (sin teclear valores)."""
    if v is None:
        return None
    try:
        x = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if x != x or x in (float("inf"), float("-inf")):
        return None
    return x


def chart_tierB_range(tier: pd.DataFrame) -> Path:
    """Tier B: rango min-max y mediana temporal vs larga por separado.

    3 barras (Sopela 19, Zarautz 15, Santurtzi 11) desde
    `mongo_tier_confianza.csv`; cada barra con min-max y las dos medianas
    con su n_precio visible. Etiqueta `indicativo`: no es ranking firme.
    Nunca promedia temporal + larga.
    """
    b = tier[tier["tier"] == "B"].copy()
    b["n_anuncios"] = b["n_anuncios"].astype(int)
    b = b.sort_values("n_anuncios", ascending=False)
    assert len(b) == 3, b["nombre"].tolist()
    nombres = [str(n) for n in b["nombre"]]
    etiquetas = [f"{n} (n={int(k)})" for n, k in zip(nombres, b["n_anuncios"])]

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ymin = min(float(b["min_precio"].min()), 0.0)
    ymax = float(b["max_precio"].max())
    for y, (_, r) in enumerate(b.iterrows()):
        lo, hi = _num(r["min_precio"]), _num(r["max_precio"])
        assert lo is not None and hi is not None
        ax.barh(y, hi - lo, left=lo, color=ACCENT, alpha=0.22,
                edgecolor=ACCENT, height=0.5, linewidth=1.2)
        mt, ml = _num(r["mediana_precio_temporal"]), _num(r["mediana_precio_larga"])
        nt, nl = int(r["n_precio_temporal"]), int(r["n_precio_larga"])
        if mt is not None:
            ax.plot(mt, y, marker="o", color=NAVY, markersize=7, linestyle="none")
            ax.annotate(f"temporal {_es(mt, 0)} (n={nt})", (mt, y),
                        xytext=(0, 13), textcoords="offset points",
                        ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
        if ml is not None:
            ax.plot(ml, y, marker="D", color=TEAL, markersize=6, linestyle="none")
            ax.annotate(f"larga {_es(ml, 0)} (n={nl})", (ml, y),
                        xytext=(0, -20), textcoords="offset points",
                        ha="center", fontsize=8.5, color=TEAL, fontweight="bold")
    ax.set_yticks(range(len(b)), etiquetas)
    ax.invert_yaxis()
    ax.set_xlim(ymin, ymax * 1.05)
    ax.set_xlabel("precio anuncio (eur)")
    ax.set_title("Tier B — rango min–max y mediana por modalidad · indicativo",
                 loc="left", fontsize=12)
    ax.text(0.99, -0.14, "indicativo (n 10–29): representación de rango, no ranking firme",
            transform=ax.transAxes, ha="right", fontsize=9, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "chart_tierB_range.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_mapa_tier(geojson_path: Path, tier: pd.DataFrame,
                    esfuerzo: pd.DataFrame) -> Path:
    """Coroplético 4 niveles A/B/C/D como SVG desde el GeoJSON 252.

    Join estricto por `codigo_ine` (sin match -> nulo, sin inventar).
    Capas por `metodo_imputacion`/`is_imputed` del CSV de esfuerzo:
    oficial 159 / IDW 93 / contexto 252; oficial con borde sólido e IDW
    con borde discontinuo. Proyección equirectangular simple.
    """
    import json
    import math

    geo = json.loads(geojson_path.read_text(encoding="utf-8-sig"))
    features = geo["datos"]["features"]
    assert len(features) == 252, len(features)

    def _norm(code: object) -> str:
        s = str(code or "").strip()
        return s.zfill(5)

    tier_map = {_norm(r["codigo_ine"]): str(r["tier"])
                for _, r in tier.iterrows()}
    capa_map = {}
    for _, r in esfuerzo.iterrows():
        met = str(r.get("metodo_imputacion") or "")
        capa_map[_norm(r.get("_id"))] = "oficial" if met == "oficial" else "idw"

    # Cromas de tier + borde por capa (oficial sólido / IDW discontinuo).
    relleno = {"A": TEAL, "B": ACCENT, "C": "#D8D1C2", "D": PAPER}
    unidas = 0
    n_oficial = n_idw = 0
    for f in features:
        code = _norm(f["properties"].get("codigo_ine"))
        f["_tier"] = tier_map.get(code)
        if f["_tier"] is not None:
            unidas += 1
        f["_capa"] = capa_map.get(code)
        if f["_capa"] == "oficial":
            n_oficial += 1
        elif f["_capa"] == "idw":
            n_idw += 1
    assert unidas == 252, unidas
    assert n_oficial + n_idw == 252, (n_oficial, n_idw)

    def _rings(geom) -> list[list[list[list[float]]]]:
        if geom is None:
            return []
        if geom["type"] == "Polygon":
            return [geom["coordinates"]]
        return geom["coordinates"]

    coords = [c for f in features for poly in _rings(f["geometry"])
              for ring in poly for c in ring]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    lat0 = (min(lats) + max(lats)) / 2
    lon_min, lat_max = min(lons), max(lats)
    kx = math.cos(math.radians(lat0))

    W, H, pad = 960, 560, 18
    dx = (max(lons) - lon_min) * kx
    dy = lat_max - min(lats)
    s = min((W - 2 * pad) / dx, (H - 2 * pad) / dy)

    def _pt(lon: float, lat: float) -> tuple[float, float]:
        return (pad + (lon - lon_min) * kx * s, pad + (lat_max - lat) * s)

    def _simplificar(pts: list[tuple[float, float]], eps: float = 0.5) -> list[tuple[float, float]]:
        """Deduplica + Douglas-Peucker (eps en px SVG). No toca clasificación."""
        ded: list[tuple[float, float]] = []
        for p in pts:
            if not ded or p != ded[-1]:
                ded.append(p)
        if len(ded) < 3:
            return ded
        def _perp(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
            dx, dy = x2 - x1, y2 - y1
            if dx == 0 and dy == 0:
                return math.hypot(px - x1, py - y1)
            return abs(dy * px - dx * py + x2 * y1 - y2 * x1) / math.hypot(dx, dy)
        keep = [False] * len(ded)
        keep[0] = keep[-1] = True
        def _rec(a: int, b: int) -> None:
            if b - a < 2:
                return
            x1, y1 = ded[a]
            x2, y2 = ded[b]
            dmax, idx = 0.0, -1
            for i in range(a + 1, b):
                d = _perp(ded[i][0], ded[i][1], x1, y1, x2, y2)
                if d > dmax:
                    dmax, idx = d, i
            if dmax > eps and idx != -1:
                keep[idx] = True
                _rec(a, idx)
                _rec(idx, b)
        _rec(0, len(ded) - 1)
        return [ded[i] for i in range(len(ded)) if keep[i]]

    partes: list[str] = []
    for f in features:
        rell = relleno.get(f["_tier"] or "", PAPER)
        dash = ' stroke-dasharray="3,2"' if f["_capa"] == "idw" else ""
        for poly in _rings(f["geometry"]):
            for ring in poly:
                _pts = [_pt(lon, lat) for lon, lat in ring]
                _simp = _simplificar(_pts)
                path = "M" + "L".join(f"{pt[0]:.1f} {pt[1]:.1f}" for pt in _simp) + " Z"
                partes.append(
                    f'<path d="{path}" fill="{rell}" fill-rule="evenodd" '
                    f'stroke="{INK}" stroke-width="0.6"{dash}/>'
                )

    # Leyenda de tiers (conteos desde el CSV, no tecleados).
    conteo = pd.Series([f["_tier"] for f in features]).value_counts()
    leyenda = []
    lx = W - 218
    for i, t in enumerate(("A", "B", "C", "D")):
        yy = 96 + i * 26
        leyenda.append(
            f'<rect x="{lx}" y="{yy}" width="14" height="14" '
            f'fill="{relleno[t]}" stroke="{INK}"/>\n'
            f'<text x="{lx + 22}" y="{yy + 12}" font-size="13" fill="{INK}">'
            f'Tier {t} · {int(conteo.get(t, 0))}</text>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">\n'
        f'<text x="{pad}" y="30" font-size="16" fill="{INK}">'
        f'Tier por municipio (A/B/C/D) · 252/252 clasificados</text>\n'
        + "\n".join(partes) + "\n"
        + "\n".join(leyenda) + "\n"
        f'<text x="{lx}" y="66" font-size="13" fill="{INK}">capas</text>\n'
        f'<text x="{lx}" y="212" font-size="13" fill="{INK}">oficial {n_oficial} (borde sólido)</text>\n'
        f'<text x="{lx}" y="232" font-size="13" fill="{INK}">IDW {n_idw} (borde discontinuo)</text>\n'
        f'<text x="{lx}" y="252" font-size="13" fill="{INK}">contexto 252</text>\n'
        f'<text x="{lx}" y="292" font-size="14" font-weight="bold" fill="{ACCENT}">'
        f'252 contextual sobre 159</text>\n</svg>\n'
    )
    ruta = ASSETS / "chart_mapa_tier.svg"
    ruta.write_text(svg, encoding="utf-8")
    return ruta


def chart_effort_vs_n(esfuerzo: pd.DataFrame) -> Path:
    """Burbuja X n_anuncios, Y esfuerzo 18-34, tamaño n_precio.

    Exactamente 4 puntos: solo Tier A rankeables (n>=30). Banda vertical
    `n_insuficiente` para n<30 sin puntos ni ordenación.
    """
    rank = esfuerzo[esfuerzo["estado"] == "rankeable"].copy()
    assert len(rank) == 4, sorted(rank["nombre"].tolist())
    rank["n_anuncios"] = rank["n_anuncios"].astype(int)
    rank["esfuerzo"] = rank["esfuerzo_joven_pct_18_34"].astype(float)
    rank["n_precio"] = rank["n_precio"].astype(int)

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.axvspan(0, 30, color=GRID, alpha=0.55, zorder=0)
    ax.text(15, ax.get_ylim()[0] if False else 0, "", fontsize=9)
    ax.text(15, float(rank["esfuerzo"].min()) - 6,
            "n_insuficiente\nmuestra insuficiente\n(sin ranking)",
            ha="center", va="top", fontsize=9.5, color=INK)
    tamanios = rank["n_precio"].astype(float) * 2.2
    ax.scatter(rank["n_anuncios"], rank["esfuerzo"], s=tamanios,
               color=ACCENT, alpha=0.55, edgecolor=NAVY, linewidth=1.4, zorder=3)
    for _, r in rank.iterrows():
        ax.annotate(f"{r['nombre']} (n={int(r['n_anuncios'])})",
                    (r["n_anuncios"], r["esfuerzo"]),
                    xytext=(8, 10), textcoords="offset points",
                    fontsize=9.5, color=NAVY, fontweight="bold")
    ax.set_xlim(0, float(rank["n_anuncios"].max()) * 1.12)
    ax.set_xlabel("n_anuncios")
    ax.set_ylabel("esfuerzo joven 18-34 (%)")
    ax.set_title("Esfuerzo vs muestra — solo 4 Tier A rankeables (n≥30)",
                 loc="left", fontsize=12)
    ax.axhline(30, color=RED, linewidth=1.6, linestyle="--")
    ley = ax.scatter([], [], s=float(rank["n_precio"].median()) * 2.2,
                     color=ACCENT, alpha=0.55, edgecolor=NAVY)
    ax.legend([ley], ["tamaño = n_precio"], fontsize=9, loc="upper left",
              frameon=False)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "chart_effort_vs_n.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def chart_habitaciones_medianas(
    habitaciones: pd.DataFrame, tier: pd.DataFrame
) -> Path:
    """Residencia (temporal/larga por separado) vs habitaciones por municipio.

    Lee `mongo_habitaciones_por_municipio.csv` (9 filas, 201 anuncios) y
    `mongo_tier_confianza.csv` (252 filas); valores Mongo, nunca tecleados.
    Dibuja tres series nunca agregadas ni promediadas: residencia temporal,
    residencia larga y habitaciones (una barra por municipio y serie).
    Cada barra de habitaciones muestra `mediana_precio_eur` con min-max
    (`min_precio_eur`/`max_precio_eur`) y `n_precio` visible. Solo Bilbao
    (96) y Donostia (66) con n>=30 sostienen comparación firme; el resto
    (Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2,
    Eibar 1) es indicativo/n_insuficiente, sin ranking ni imputación.
    """
    hab = habitaciones.copy()
    hab["codigo_ine"] = hab["codigo_ine"].astype(str).str.zfill(5)
    hab["n"] = hab["n"].astype(int)
    hab["n_precio"] = hab["n_precio"].astype(int)
    # Orden por muestra de habitaciones (n desc, código asc para empates).
    hab = hab.sort_values(["n", "codigo_ine"], ascending=[False, True]).reset_index(drop=True)
    assert len(hab) == 9, hab["codigo_ine"].tolist()
    assert sorted(hab["n"].tolist(), reverse=True) == [96, 66, 12, 11, 8, 3, 2, 2, 1], sorted(hab["n"].tolist(), reverse=True)

    tier = tier.copy()
    tier["codigo_ine"] = tier["codigo_ine"].astype(str).str.zfill(5)
    tmap = {str(r["codigo_ine"]): r for _, r in tier.iterrows()}

    def _etiqueta_mun(nombre: object) -> str:
        s = str(nombre or "sin nombre").strip()
        s = s.replace(" - ", "-").replace(" / ", " / ")
        return s

    etiquetas: list[str] = []
    for _, r in hab.iterrows():
        mun = _etiqueta_mun(r["municipio"])
        n = int(r["n_precio"])
        estado = "firme" if n >= 30 else "indicativo"
        etiquetas.append(f"{mun} (n={n} · {estado})")

    n_mun = len(hab)
    fig, ax = plt.subplots(figsize=(9.8, 5.8))
    # Tres barras por municipio con hueco entre grupos.
    paso = 1.0
    off_h, off_t, off_l = -0.34, 0.0, 0.34
    alt_barra = 0.30
    for i, (_, r) in enumerate(hab.iterrows()):
        code = str(r["codigo_ine"])
        y0 = i * 3 * paso
        tr = tmap.get(code)
        med_h = _num(r["mediana_precio_eur"])
        lo_h = _num(r["min_precio_eur"])
        hi_h = _num(r["max_precio_eur"])
        n_h = int(r["n_precio"])
        # Habitaciones (mediana + min-max).
        if med_h is not None:
            ax.barh(y0 + off_h, med_h, color=ACCENT, height=alt_barra,
                    edgecolor=ACCENT, linewidth=1.0, zorder=3)
            if lo_h is not None and hi_h is not None and hi_h >= med_h >= lo_h:
                ax.errorbar(med_h, y0 + off_h, xerr=[[med_h - lo_h], [hi_h - med_h]],
                            fmt="none", ecolor=NAVY, elinewidth=1.4, capsize=4, zorder=4)
            ax.text(med_h + 45, y0 + off_h,
                    f"{_es(med_h, 0)} (n_precio={n_h}) min–max {_es(lo_h or 0, 0)}–{_es(hi_h or 0, 0)}",
                    va="center", fontsize=8, color=INK)
        else:
            ax.text(45, y0 + off_h, "sin precio", va="center", fontsize=8, color=MUTED)
        # Residencia temporal (separada).
        if tr is not None:
            mt = _num(tr.get("mediana_precio_temporal"))
            nt = tr.get("n_precio_temporal")
            nt_i = int(nt) if str(nt).strip() not in ("", "nan", "None") else 0
        else:
            mt, nt_i = None, 0
        if mt is not None:
            ax.barh(y0 + off_t, mt, color=NAVY, height=alt_barra,
                    edgecolor=NAVY, linewidth=1.0, zorder=3)
            ax.text(mt + 45, y0 + off_t, f"{_es(mt, 0)} (n_precio={nt_i})",
                    va="center", fontsize=8, color=NAVY)
        else:
            ax.text(45, y0 + off_t, "sin precio municipal", va="center", fontsize=8, color=MUTED)
        # Residencia larga (separada).
        if tr is not None:
            ml = _num(tr.get("mediana_precio_larga"))
            nl = tr.get("n_precio_larga")
            nl_i = int(nl) if str(nl).strip() not in ("", "nan", "None") else 0
        else:
            ml, nl_i = None, 0
        if ml is not None:
            ax.barh(y0 + off_l, ml, color=TEAL, height=alt_barra,
                    edgecolor=TEAL, linewidth=1.0, zorder=3)
            ax.text(ml + 45, y0 + off_l, f"{_es(ml, 0)} (n_precio={nl_i})",
                    va="center", fontsize=8, color=TEAL)
        else:
            ax.text(45, y0 + off_l, "sin precio municipal", va="center", fontsize=8, color=MUTED)

    ax.set_yticks([i * 3 * paso for i in range(n_mun)], etiquetas, fontsize=9)
    ax.invert_yaxis()
    # Eje cubre todas las medianas; los máx atípicos quedan anotados en texto.
    meds = [float(_num(v) or 0) for v in list(hab["mediana_precio_eur"]) + list(tier["mediana_precio_temporal"].dropna()) + list(tier["mediana_precio_larga"].dropna()) if _num(v) is not None]
    xmax = max(meds) * 1.25 if meds else 2500
    ax.set_xlim(0, max(xmax, 2800))
    ax.set_xlabel("mediana precio anuncio (eur) · barras nunca agregadas")
    ax.set_title(
        "Residencia vs habitaciones — mediana por municipio",
        loc="left", fontsize=13,
    )
    ax.text(
        0.99, -0.09,
        "temporal y larga nunca se promedian · habitaciones: mediana + min–max + n_precio",
        transform=ax.transAxes, ha="right", fontsize=9, color=MUTED,
    )
    ax.text(
        0.99, -0.13,
        "firme solo Bilbao (96) y Donostia (66) n≥30 · resto indicativo n_insuficiente, sin ranking",
        transform=ax.transAxes, ha="right", fontsize=9, color=MUTED,
    )
    from matplotlib.patches import Patch
    ax.legend(
        handles=[
            Patch(color=ACCENT, label="habitaciones"),
            Patch(color=NAVY, label="residencia temporal"),
            Patch(color=TEAL, label="residencia larga"),
        ],
        fontsize=9, loc="lower right", frameon=False, ncols=3,
    )
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    ruta = ASSETS / "chart_habitaciones_medianas.svg"
    fig.savefig(ruta, format="svg", transparent=True)
    plt.close(fig)
    return ruta


def main() -> int:
    df = pd.read_csv(
        RES / "mongo_esfuerzo_por_municipio.csv",
        encoding="utf-8-sig",
        dtype={"_id": str},
    )
    esf_col = "esfuerzo_joven_pct_18_34"
    oficial = df[df["tiene_alquiler_oficial"].astype(str).str.lower() == "true"]
    esf_of = oficial[esf_col].dropna()
    mediana_of = float(esf_of.median())
    n30_of = int((esf_of > 30).sum())
    esf_all = df[esf_col].dropna()
    mediana_all = float(esf_all.median())
    n30_all = int((esf_all > 30).sum())

    medias_terr = oficial.groupby("territorio")[esf_col].median()
    ns_terr = oficial.groupby("territorio").size()

    boot = pd.read_csv(
        RES / "bootstrap_robustos.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    sens = pd.read_csv(RES / "sensibilidad_idw.csv", encoding="utf-8-sig")
    totales = {str(k): int(v) for k, v in df.set_index("_id")["n_anuncios"].items()}

    tension = df["tension_categoria"].value_counts()
    vpo = pd.read_csv(ROOT / "data" / "procesado" / "vpo_municipal.csv", encoding="utf-8-sig")

    tramos = {
        "< 25 %": int((esf_of < 25).sum()),
        "25-30 %": int(((esf_of >= 25) & (esf_of <= 30)).sum()),
        "> 30 %": int((esf_of > 30).sum()),
    }
    assert sum(tramos.values()) == len(esf_of), tramos
    n_idw = int((df["is_imputed"].astype(str).str.lower() == "true").sum())
    assert n_idw == len(df) - len(esf_of), (n_idw, len(df), len(esf_of))
    print("tramos:", tramos, "| idw:", n_idw)

    n_anuncios = int(df["n_anuncios"].sum())

    chart_histograma(esf_of, mediana_of, n30_of, len(esf_of))
    chart_territorios(medias_terr, ns_terr)
    chart_tramos(tramos, n_idw)
    chart_robustos(boot, totales)
    chart_sensibilidad(sens)
    decor_topo()
    decor_trama(n_anuncios)

    tier = pd.read_csv(
        RES / "mongo_tier_confianza.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    chart_tierB_range(tier)
    chart_mapa_tier(
        ROOT / "data" / "procesado" / "municipios_euskadi_252.geojson",
        tier, df,
    )
    chart_effort_vs_n(df)
    habitaciones = pd.read_csv(
        RES / "mongo_habitaciones_por_municipio.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    chart_habitaciones_medianas(habitaciones, tier)

    fila = boot.set_index("municipio")
    vals = {
        "mediana_oficial": _es(mediana_of),
        "n30_oficial": n30_of,
        "pct_oficial": _es(100 * n30_of / len(esf_of), 1),
        "n_oficial": len(esf_of),
        "n_oficial_menos_no": len(esf_of) - n30_of,
        "mediana_global": _es(mediana_all),
        "n30_global": n30_all,
        "pct_global": _es(100 * n30_all / len(esf_all), 1),
        "n_global": len(esf_all),
        "tramo_margen": tramos["< 25 %"],
        "tramo_justo": tramos["25-30 %"],
        "tramo_no": tramos["> 30 %"],
        "n_idw": n_idw,
        "n_anuncios": n_anuncios,
        "tension_alta": int(tension.get("alta", 0)),
        "tension_media": int(tension.get("media", 0)),
        "tension_baja": int(tension.get("baja", 0)),
        "vpo_con_dato": int(vpo["vpo_terminadas_por_mil"].notna().sum()),
        "vpo_total": len(vpo),
        "vpo_max": _es(float(vpo["vpo_terminadas_por_mil"].max())),
        "vpo_max_mun": str(vpo.loc[vpo["vpo_terminadas_por_mil"].idxmax(), "municipio"]),
    }
    for nombre in ("Bilbao", "Donostia", "Getxo", "Vitoria-Gasteiz"):
        clave = {"Donostia": "Donostia", "Vitoria-Gasteiz": "Vitoria"}.get(nombre, nombre)
        r = fila.loc[nombre]
        vals[f"{clave.lower()}_esf"] = _es(float(r["esfuerzo_canonico_pct"]))
        vals[f"{clave.lower()}_n"] = totales.get(str(r["codigo_ine"]), 0)
        vals[f"{clave.lower()}_ic"] = f"{_es(float(r['ic95_inf']))}-{_es(float(r['ic95_sup']))} %"

    # Tier B: pie con el n de cada mediana (desde el CSV, sin teclear).
    for _, r in tier[tier["tier"] == "B"].iterrows():
        clave = str(r["nombre"]).lower()
        vals[f"tierB_{clave}_n"] = int(r["n_anuncios"])
        vals[f"tierB_{clave}_med_t"] = _es(float(r["mediana_precio_temporal"]), 0)
        vals[f"tierB_{clave}_n_t"] = int(r["n_precio_temporal"])
        vals[f"tierB_{clave}_med_l"] = _es(float(r["mediana_precio_larga"]), 0)
        vals[f"tierB_{clave}_n_l"] = int(r["n_precio_larga"])

    plantilla = (OUT / "index.template.html").read_text(encoding="utf-8")

    def _sub(m: re.Match[str]) -> str:
        return str(vals[m.group(1)])

    try:
        html = re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", _sub, plantilla)
    except KeyError as exc:
        raise SystemExit(f"Placeholder sin valor: {exc}") from exc
    resto = re.findall(r"\{\{[^}]*\}\}", html)
    if resto:
        raise SystemExit(f"Placeholders sin resolver: {sorted(set(resto))}")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"OK index.html ({len(html)} bytes) y 11 SVG en {ASSETS}")
    print(f"oficial: {vals['mediana_oficial']} % · {vals['n30_oficial']}/{vals['n_oficial']} > 30")
    print(f"global: {vals['mediana_global']} % · {vals['n30_global']}/{vals['n_global']} > 30")
    print(f"decor: topo + trama de {n_anuncios} anuncios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
