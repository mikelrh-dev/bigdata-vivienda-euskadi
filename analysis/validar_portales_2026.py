"""Sensibilidad de la capa 2026 al portal de origen de los anuncios.

Los 287 anuncios validos vienen de tres fuentes (fotocasa, pisos, realtyapi).
Este script mide cuanto cambia el esfuerzo 2026 al excluir realtyapi, que es la
fuente con mayor precio/m2 y la que mas se mueve entre municipios.

No toca raw, no cambia el CSV de esfuerzo (el titular se queda donde esta): solo
publica la sensibilidad para poder defenderla o corregirla con datos en mano.

Lee:
  - data/procesado/anuncios_vivienda_residencial_filtrado.csv (via helper unico)
  - data/procesado/esfuerzo_mercado_2026.csv (salario ajustado 2026)

Guarda:
  - data/resultados/validacion_portales_2026.csv

Uso:
    python analysis/validar_portales_2026.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "transform"))

from _anuncios_2026 import cargar_anuncios_2026  # noqa: E402

PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"
MERCADO = PROC / "esfuerzo_mercado_2026.csv"
OUT = RES / "validacion_portales_2026.csv"

CAVEAT = (
    "sensibilidad al portal, no alquiler oficial; realtyapi tiene mayor precio/m2 "
    "y su efecto cambia de signo por municipio, lo que apunta a mezcla de producto"
)


def _salario_18_34() -> float:
    d = pd.read_csv(MERCADO, encoding="utf-8-sig", dtype=str)
    s = pd.to_numeric(d["salario_joven_2026_ajustado_18_34_eur_mes"], errors="coerce")
    return float(s.median())


def main() -> int:
    df, meta = cargar_anuncios_2026()
    v = df[df["anuncio_valido"]].copy()
    sal = _salario_18_34()
    v["esf"] = v["precio_eur"] / sal * 100

    print(f"Anuncios validos: {len(v)} (de {meta['n_usados']} usados en la capa)")
    print("Por portal:")
    for portal, g in v.groupby("portal"):
        print(f"   {portal:<10} n={len(g):3d}  mediana={g['precio_eur'].median():7.0f} EUR  "
              f"EUR/m2={g['precio_m2'].median():5.2f}  m2={g['superficie_m2'].median():4.0f}")

    filas = []
    for (code, nombre), g in v.groupby(["codigo_ine", "municipio"], sort=True):
        sin_realty = g[g["portal"] != "realtyapi"]
        med_todos = g["esf"].median()
        med_sin = sin_realty["esf"].median() if len(sin_realty) else float("nan")
        filas.append({
            "codigo_ine": code,
            "nombre_canonico": nombre,
            "n_total": len(g),
            "n_fotocasa": int((g["portal"] == "fotocasa").sum()),
            "n_pisos": int((g["portal"] == "pisos").sum()),
            "n_realtyapi": int((g["portal"] == "realtyapi").sum()),
            "precio_mediana_todos_eur_mes": round(g["precio_eur"].median(), 2),
            "precio_mediana_sin_realtyapi_eur_mes": (
                round(sin_realty["precio_eur"].median(), 2) if len(sin_realty) else None),
            "esfuerzo_mediana_todos_pct_18_34": round(med_todos, 2),
            "esfuerzo_mediana_sin_realtyapi_pct_18_34": (
                round(med_sin, 2) if pd.notna(med_sin) else None),
            "delta_pp_sin_realtyapi": (
                round(med_sin - med_todos, 2) if pd.notna(med_sin) else None),
            "tiene_muestra_suficiente": len(g) >= 5,
            "caveat": CAVEAT,
        })

    out = pd.DataFrame(filas)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    grandes = out[out["n_total"] >= 5].copy()
    global_todos = grandes["esfuerzo_mediana_todos_pct_18_34"].median()
    con_ambos = grandes.dropna(subset=["esfuerzo_mediana_sin_realtyapi_pct_18_34"])
    global_sin = con_ambos["esfuerzo_mediana_sin_realtyapi_pct_18_34"].median()
    print(f"\nOK: {OUT.name} ({len(out)} municipios)")
    print(f"   mediana de medianas (n>=5): todos={global_todos:.1f} %  "
          f"sin realtyapi={global_sin:.1f} %  (n={len(con_ambos)} municipios)")
    mov = con_ambos.reindex(con_ambos["delta_pp_sin_realtyapi"].abs()
                            .sort_values(ascending=False).index).head(5)
    print("   mayores desplazamientos al quitar realtyapi:")
    for _, r in mov.iterrows():
        print(f"     {r['nombre_canonico']:<26} {r['esfuerzo_mediana_todos_pct_18_34']:6.1f} % -> "
              f"{r['esfuerzo_mediana_sin_realtyapi_pct_18_34']:6.1f} % "
              f"({r['delta_pp_sin_realtyapi']:+.1f} pp, n={int(r['n_total'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
