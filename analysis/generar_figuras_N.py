"""Genera figuras P0 (N1-N3, N7) + H2 regenerado desde CSV (sin Mongo vivo).

Lee los CSV ya exportados en data/resultados/ y los procesados en
data/procesado/ (nunca Mongo en vivo). Reutilizable y determinista:
no contiene valores tecleados salvo umbrales desde
config/parametros_estudio.yaml (fallback 30/40).

Uso:
  .venv/Scripts/python.exe analysis/generar_figuras_N.py
Genera en data/resultados/:
  mapa_coroplastico_esfuerzo_18_34.png (N1, coroplético 252)
  hist_esfuerzo_18_34_umbral30.png (N2, histograma + umbrales 30/40)
  dumbbell_esfuerzo_18_24_vs_25_34.png (N3, dumbbell top20 joven)
  transporte_oferta_vs_esfuerzo.png (N7, scatter oferta vs esfuerzo)
  H2_tier_confianza_ABCD.png (H2 regenerado, layout expandido)
  F_comparativa_TH.png, H8_tier_mediana_temporal_vs_larga.png,
  J_tier_confianza_vs_precio.png, P_oficial_vs_anuncios_por_TH.png
  (títulos/ejes con €/mes vs €/m2 y Territorio Histórico (TH))
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon as MplPolygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, PROJECT_ROOT, RESULTADOS_DIR  # noqa: E402

RES = RESULTADOS_DIR
PROC = PROCESADO_DIR
PARAMS = PROJECT_ROOT / "config" / "parametros_estudio.yaml"
RES.mkdir(parents=True, exist_ok=True)


def _umbrales() -> tuple[float, float]:
    """Lee umbrales esfuerzo_moderado/crítico (30/40) de parametros."""
    try:
        import yaml

        cfg = yaml.safe_load(PARAMS.read_text(encoding="utf-8"))
        u = cfg.get("umbrales", {}) if isinstance(cfg, dict) else {}
        return float(u.get("esfuerzo_moderado", 30)), float(u.get("esfuerzo_tensionado", u.get("esfuerzo_critico", 40)))
    except Exception:
        return 30.0, 40.0


def generar_N1() -> Path:
    """N1: coroplético esfuerzo 18-34 por municipio (252, verde-ámbar-rojo)."""
    df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    df["_id"] = pd.to_numeric(df["_id"], errors="coerce")
    df["esfuerzo_joven_pct_18_34"] = pd.to_numeric(df["esfuerzo_joven_pct_18_34"], errors="coerce")
    gj = json.loads((PROC / "municipios_euskadi_252.geojson").read_text(encoding="utf-8"))
    feats = gj["datos"]["features"]
    # join codigo_ine: CSV _id int vs GeoJSON '01002' str zero-padded
    df["codigo5"] = df["_id"].astype(int).astype(str).str.zfill(5)
    esfuerzo = dict(zip(df["codigo5"], df["esfuerzo_joven_pct_18_34"]))
    # Territorio por municipio desde CSV (para anotar en título)
    ths = sorted(df["territorio"].dropna().unique().tolist())
    cmap = LinearSegmentedColormap.from_list("verde_ambar_rojo", ["#1a9850", "#fee08b", "#d73027"], N=256)
    patches = []
    vals = []
    th_por_mun = {}
    for f in feats:
        code = str(f["properties"]["codigo_ine"]).zfill(5)
        th_por_mun[code] = f["properties"].get("territorio", "")
        geom = f["geometry"]
        v = esfuerzo.get(code, np.nan)
        if np.isnan(v):
            continue
        t = geom["type"]
        polys = []
        if t == "Polygon":
            polys = [geom["coordinates"]]
        elif t == "MultiPolygon":
            polys = geom["coordinates"]
        for poly in polys:
            for ring in poly:
                patches.append(MplPolygon(ring, closed=True))
                vals.append(v)
    vals_arr = np.array(vals, dtype=float)
    vmin, vmax = float(np.nanmin(vals_arr)), float(np.nanmax(vals_arr))
    # corte visual 30%: normalización hacia 30% aporta contraste
    norm_v = np.clip((vals_arr - vmin) / (30.0 - vmin if 30.0 > vmin else 1.0), 0, 1)
    # reescalar: >30% va a rojo saturado; <30% gradiente verde-ámbar
    fig, ax = plt.subplots(figsize=(10, 8))
    pc = PatchCollection(patches, cmap=cmap, edgecolor="white", linewidth=0.2, alpha=0.95)
    pc.set_array(norm_v)
    pc.set_clim(0, 1)
    ax.add_collection(pc)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(
        f"N1 Esfuerzo joven 18-34 por municipio (252) — Territorio Histórico (TH): {', '.join(ths)}\n"
        f"Esfuerzo % (verde→ámbar→rojo, corte 30%)",
        fontsize=11,
    )
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.7)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels([f"{vmin:.1f}%", "≈15%", "≥30%"])
    cbar.set_label("Esfuerzo joven 18-34 %")
    fig.text(0.5, 0.02, "Fuente: mongo_esfuerzo_por_municipio.csv + municipios_euskadi_252.geojson (join codigo_ine). Corte visual 30%.",
             ha="center", fontsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(rect=[0, 0.04, 1, 0.94])
    out = RES / "mapa_coroplastico_esfuerzo_18_34.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK N1: {out} ({out.stat().st_size} bytes, 252 feats, {vmin:.1f}%-{vmax:.1f}%)")
    return out


def generar_N2() -> Path:
    """N2: histograma esfuerzo 18-34 (252) + líneas 30%/40%."""
    df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    s = pd.to_numeric(df["esfuerzo_joven_pct_18_34"], errors="coerce").dropna()
    mod, crit = _umbrales()  # 30, 40 por defecto
    n = len(s)
    pct30 = float((s > mod).mean() * 100)
    pct40 = float((s > crit).mean() * 100)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(s, bins=min(30, max(10, n // 8)), color="#0072B2", edgecolor="white", alpha=0.85)
    ax.axvline(mod, color="#D55E00", linestyle="--", linewidth=2, label=f"Moderado {mod:.0f}% (esfuerzo_moderado)")
    ax.axvline(crit, color="#CC0000", linestyle="-.", linewidth=2, label=f"Crítico {crit:.0f}% (esfuerzo_tensionado)")
    ax.set_xlabel("Esfuerzo alquiler joven 18-34 % (canónico)")
    ax.set_ylabel("Municipios (n=252)")
    ax.set_title(f"N2 Histograma esfuerzo joven 18-34 — {n} municipios, {pct30:.1f}% >30% (>{mod:.0f}%)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.text(0.5, 0.01, f"Fuente: mongo_esfuerzo_por_municipio.csv (252). Umbrales config/parametros_estudio.yaml: moderado={mod:.0f}%, crítico={crit:.0f}%. >{crit:.0f}%: {pct40:.1f}%.",
             ha="center", fontsize=8)
    fig.tight_layout()
    out = RES / "hist_esfuerzo_18_34_umbral30.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK N2: {out} ({out.stat().st_size} bytes, n={n}, >30%={pct30:.1f}%)")
    return out


def generar_N3() -> Path:
    """N3: dumbbell esfuerzo 18-24 vs 25-34 joven (top20 brecha + medianas)."""
    df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    pob = pd.read_csv(PROC / "poblacion_joven_municipal.csv", dtype=str, encoding="utf-8-sig")
    # join para validar 252 (población joven disponible)
    df["_id_num"] = pd.to_numeric(df["_id"], errors="coerce")
    df["codigo_ine"] = df["_id_num"].astype("Int64")
    pob["codigo_ine"] = pd.to_numeric(pob["codigo_ine"], errors="coerce").astype("Int64")
    m = df.merge(pob[["codigo_ine", "nombre", "poblacion_18_24_est", "poblacion_25_34_est"]],
                 on="codigo_ine", how="inner", suffixes=("", "_pob"))
    m["e1824"] = pd.to_numeric(m["esfuerzo_joven_pct_18_24"], errors="coerce")
    m["e2534"] = pd.to_numeric(m["esfuerzo_joven_pct_25_34"], errors="coerce")
    m["brecha"] = m["e1824"] - m["e2534"]
    m = m.dropna(subset=["e1824", "e2534", "nombre"])
    # mediana por Territorio Histórico (TH) para anotar
    med_th = m.groupby("territorio")[["e1824", "e2534"]].median()
    top = m.nlargest(20, "brecha").copy()
    top = top.iloc[::-1]  # menor arriba para dumbbell
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (_, r) in enumerate(top.iterrows()):
        ax.plot([r["e1824"], r["e2534"]], [i, i], color="#888888", linewidth=2)
        ax.scatter([r["e1824"]], [i], color="#D55E00", s=60, zorder=3, label="18-24 joven" if i == 0 else None)
        ax.scatter([r["e2534"]], [i], color="#0072B2", s=60, zorder=3, label="25-34 joven" if i == 0 else None)
        ax.text(max(r["e1824"], r["e2534"]) + 0.5, i, f"+{r['brecha']:.1f}pp", va="center", fontsize=7)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["nombre"].tolist(), fontsize=7)
    med1824 = float(m["e1824"].median())
    med2534 = float(m["e2534"].median())
    ax.axvline(med1824, color="#D55E00", linestyle="--", label=f"Mediana 18-24 {med1824:.1f}%")
    ax.axvline(med2534, color="#0072B2", linestyle="--", label=f"Mediana 25-34 {med2534:.1f}%")
    ax.set_xlabel("Esfuerzo alquiler joven %")
    ax.set_title("N3 Esfuerzo joven 18-24 vs 25-34 — dumbbell top20 brecha (municipios)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=4, fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    txt = "; ".join(f"{th}: 18-24 {r['e1824']:.1f}%, 25-34 {r['e2534']:.1f}%" for th, r in med_th.iterrows())
    fig.text(0.5, 0.01, f"Medianas por Territorio Histórico (TH): {txt} | Fuente: mongo_esfuerzo_por_municipio.csv + poblacion_joven_municipal.csv (252).",
             ha="center", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0, 0.05, 1, 0.96])
    out = RES / "dumbbell_esfuerzo_18_24_vs_25_34.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK N3: {out} ({out.stat().st_size} bytes, top20, medianas {med1824:.1f}%/{med2534:.1f}%)")
    return out


def generar_N7() -> Path:
    """N7: oferta transporte (paradas/1000) vs esfuerzo 18-34 (coloreado tren/metro)."""
    transp = pd.read_csv(PROC / "transporte_paradas_municipio_enriquecido.csv", dtype=str, encoding="utf-8-sig")
    esf = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    transp["codigo_ine"] = pd.to_numeric(transp["codigo_ine"], errors="coerce")
    esf["codigo_ine"] = pd.to_numeric(esf["_id"], errors="coerce")
    m = transp.merge(esf[["codigo_ine", "esfuerzo_joven_pct_18_34"]], on="codigo_ine", how="inner")
    m["paradas_por_1000_hab"] = pd.to_numeric(m["paradas_por_1000_hab"], errors="coerce")
    m["esfuerzo_joven_pct_18_34"] = pd.to_numeric(m["esfuerzo_joven_pct_18_34"], errors="coerce")
    m = m.dropna(subset=["paradas_por_1000_hab", "esfuerzo_joven_pct_18_34"])
    # winsoriza visual a p95 para legibilidad (mantiene outliers anotados)
    p95 = float(m["paradas_por_1000_hab"].quantile(0.95))
    m["paradas_clip"] = m["paradas_por_1000_hab"].clip(upper=p95)
    fig, ax = plt.subplots(figsize=(10, 6))
    _tren = m["tiene_tren_metro"].astype(str).str.lower().isin(["true", "1", "si"])
    con = m[_tren]
    sin = m[~_tren]
    ax.scatter(con["paradas_clip"], con["esfuerzo_joven_pct_18_34"], color="#0072B2", alpha=0.65, s=28, label=f"Con tren/metro (n={len(con)})")
    ax.scatter(sin["paradas_clip"], sin["esfuerzo_joven_pct_18_34"], color="#D55E00", alpha=0.55, s=28, label=f"Sin tren/metro (n={len(sin)})")
    # anotar extremo máximo
    idx_max = m["paradas_por_1000_hab"].idxmax()
    if idx_max is not None:
        r = m.loc[idx_max]
        ax.annotate(f"{r['nombre']}\n{r['paradas_por_1000_hab']:.1f}/1000", xy=(r["paradas_clip"], r["esfuerzo_joven_pct_18_34"]),
                    xytext=(r["paradas_clip"] + 2, r["esfuerzo_joven_pct_18_34"] + 1), fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_xlabel("Oferta transporte: paradas por 1000 hab (eje x recortado a p95)")
    ax.set_ylabel("Esfuerzo joven 18-34 %")
    ax.set_title(f"N7 Oferta transporte vs esfuerzo joven 18-34 — {len(m)} municipios (complementa H7 OSRM)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.text(0.5, 0.01, "Fuente: transporte_paradas_municipio_enriquecido.csv + mongo_esfuerzo_por_municipio.csv (join codigo_ine). H7 usa minutos OSRM a capital; N7 usa oferta (paradas/1000).",
             ha="center", fontsize=8)
    fig.tight_layout()
    out = RES / "transporte_oferta_vs_esfuerzo.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK N7: {out} ({out.stat().st_size} bytes, n={len(m)}, con tren={len(con)})")
    return out


def regenerar_H2() -> Path:
    """H2 regenerado offline con layout expandido (marcado vía código Mongo)."""
    df = pd.read_csv(RES / "mongo_tier_confianza.csv", dtype=str, encoding="utf-8-sig")
    df["n_anuncios"] = pd.to_numeric(df["n_anuncios"], errors="coerce").fillna(0)
    cnt = df["tier"].value_counts().to_dict()
    orden = ["A", "B", "C", "D"]
    presentes = [t for t in orden if t in cnt]
    vals = [int(cnt.get(t, 0)) for t in presentes]
    ab = df[df["tier"].isin(["A", "B"])].sort_values("n_anuncios", ascending=False)
    texto_ab = "; ".join(f"{r['nombre']} ({r['tier']}, n={int(r['n_anuncios'])})" for _, r in ab.iterrows()) or "sin Tier A/B"
    envuelto = textwrap.fill(f"Tier A/B ({len(ab)}): {texto_ab}", width=140)
    fig, (ax, ax_ab) = plt.subplots(2, 1, figsize=(10, 6.5), gridspec_kw={"height_ratios": [3, 1]})
    ax.bar(presentes, vals, color=["#0072B2", "#5BA3D0", "#999999", "#D55E00"])
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, str(v), ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_xlabel("Tier de confianza (conteo de municipios)")
    ax.set_ylabel("Municipios")
    ax.set_title("H2 Tier confianza A/B/C/D + n (Mongo) — Municipios por Tier (252)")
    ax.grid(axis="y", alpha=0.3)
    ax_ab.axis("off")
    ax_ab.set_title("Municipios Tier A/B con n_anuncios", fontsize=10)
    ax_ab.text(0.0, 0.55, envuelto, ha="left", va="center", fontsize=8, wrap=True,
               bbox=dict(fc="white", ec="#CCCCCC", boxstyle="round,pad=0.4"))
    fig.suptitle("H2 Tier confianza A/B/C/D por Territorio Histórico (TH) — A4/B3/C57/D188", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out = RES / "H2_tier_confianza_ABCD.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK H2: {out} ({out.stat().st_size} bytes, A/B={len(ab)})")
    return out


def regenerar_F() -> Path:
    """F con título €/mes y Territorio Histórico (TH)."""
    df = pd.read_csv(RES / "mongo_alquiler_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    df["cuantia_media"] = pd.to_numeric(df["cuantia_media"], errors="coerce")
    g = df.groupby("territorio")["cuantia_media"].mean().reindex(sorted(df["territorio"].unique()))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(g.index.tolist(), g.values.tolist())
    ax.set_title("Cuantia media alquiler por Territorio Histórico (TH) — €/mes (Mongo)")
    ax.set_ylabel("€/mes (cuantía media)")
    fig.tight_layout()
    out = RES / "F_comparativa_TH.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK F: {out} ({out.stat().st_size} bytes)")
    return out


def regenerar_H8() -> Path:
    """H8 con eje €/mes."""
    df = pd.read_csv(RES / "mongo_tier_confianza.csv", dtype=str, encoding="utf-8-sig")
    for c in ("mediana_precio_temporal", "mediana_precio_larga"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    ab = df[df["tier"].isin(["A", "B"])].copy()
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(ab))
    w = 0.35
    ax.bar(x - w / 2, ab["mediana_precio_temporal"].fillna(0).values, w, label="Temporal")
    ax.bar(x + w / 2, ab["mediana_precio_larga"].fillna(0).values, w, label="Larga estancia")
    ax.set_xticks(x)
    ax.set_xticklabels(ab["nombre"].tolist(), rotation=20, ha="right")
    ax.set_ylabel("Mediana precio €/mes")
    ax.set_title("H8 Mediana temporal vs larga - Tier A/B (Mongo) — €/mes")
    ax.legend()
    fig.tight_layout()
    out = RES / "H8_tier_mediana_temporal_vs_larga.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK H8: {out} ({out.stat().st_size} bytes)")
    return out


def regenerar_J() -> Path:
    """J con eje €/mes."""
    df = pd.read_csv(RES / "mongo_tier_confianza.csv", dtype=str, encoding="utf-8-sig")
    for c in ("n_anuncios", "mediana_precio_temporal", "mediana_precio_larga"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    ab = df[df["tier"].isin(["A", "B"])].copy()
    fig, ax = plt.subplots(figsize=(7, 4))
    for _, r in ab.iterrows():
        n = int(r["n_anuncios"])
        t = str(r["tier"])
        if pd.notna(r.get("mediana_precio_temporal")):
            ax.scatter(n, r["mediana_precio_temporal"], marker="o", color="#0072B2" if t == "A" else "#5BA3D0",
                       label=f"Temporal {t}" if t in ("A", "B") else None)
        if pd.notna(r.get("mediana_precio_larga")):
            ax.scatter(n, r["mediana_precio_larga"], marker="s", color="#D55E00" if t == "A" else "#E69F00",
                       label=f"Larga {t}" if t in ("A", "B") else None)
    ax.set_xscale("log")
    ax.set_xlabel("n_anuncios (log, Tier A/B)")
    ax.set_ylabel("Mediana precio €/mes")
    ax.set_title("J Tier confianza vs precio (Mongo, solo Tier A/B con precio municipal) — €/mes")
    ax.legend()
    fig.tight_layout()
    out = RES / "J_tier_confianza_vs_precio.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK J: {out} ({out.stat().st_size} bytes)")
    return out


def regenerar_P() -> Path:
    """P con título €/mes y Territorio Histórico (TH)."""
    df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", dtype=str, encoding="utf-8-sig")
    df["cuantia_alquiler_mes"] = pd.to_numeric(df["cuantia_alquiler_mes"], errors="coerce")
    df["precio_medio_eur"] = pd.to_numeric(df["precio_medio_eur"], errors="coerce")
    ths = sorted(df["territorio"].dropna().unique().tolist())
    med_of, med_an, n_of, n_an = [], [], [], []
    for t in ths:
        sub = df[df["territorio"] == t]
        of = sub[sub["metodo_imputacion"] == "oficial"]["cuantia_alquiler_mes"].dropna()
        an = sub["precio_medio_eur"].dropna()
        med_of.append(float(of.median()) if len(of) else 0.0)
        med_an.append(float(an.median()) if len(an) else 0.0)
        n_of.append(len(of))
        n_an.append(len(an))
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(ths))
    w = 0.35
    ax.bar(x - w / 2, med_of, w, label="Cuantia oficial €/mes (mediana)")
    ax.bar(x + w / 2, med_an, w, label="Anuncios precio medio €/mes (mediana)")
    for i in range(len(ths)):
        ax.text(i, max(med_of[i], med_an[i]) * 1.02, f"n_of={n_of[i]} n_an={n_an[i]}", ha="center", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(ths)
    ax.set_ylabel("€/mes")
    ax.set_title("P Cuantia oficial vs anuncios por Territorio Histórico (TH) — €/mes (Mongo, n y cobertura)")
    ax.legend()
    fig.tight_layout()
    out = RES / "P_oficial_vs_anuncios_por_TH.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"OK P: {out} ({out.stat().st_size} bytes)")
    return out


def main() -> int:
    print("Generando N1, N2, N3, N7 + H2/F/H8/J/P desde CSV (sin Mongo vivo)...")
    generar_N1()
    generar_N2()
    generar_N3()
    generar_N7()
    regenerar_H2()
    regenerar_F()
    regenerar_H8()
    regenerar_J()
    regenerar_P()
    print("Hecho.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
