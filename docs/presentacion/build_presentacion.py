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
    """Un pictograma de vivienda por anuncio: 759 dibujos, ni uno mas."""
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
    print(f"OK index.html ({len(html)} bytes) y 7 SVG en {ASSETS}")
    print(f"oficial: {vals['mediana_oficial']} % · {vals['n30_oficial']}/{vals['n_oficial']} > 30")
    print(f"global: {vals['mediana_global']} % · {vals['n30_global']}/{vals['n_global']} > 30")
    print(f"decor: topo + trama de {n_anuncios} anuncios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
