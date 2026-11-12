"""Mediana del esfuerzo 2026 por tipologia, calculada a nivel de anuncio.

El CSV `esfuerzo_mercado_2026_por_tipo.csv` es municipal: cada fila es un
municipio y su tipo, y el resumen por tipologia se obtiene ponderando medianas
municipales. Aqui se calcula el estimador directo: la mediana de TODOS los
anuncios de cada tipologia, con IC95 % bootstrap.

Es una capa de analisis (gold): no toca raw, no toca el canónico 2024 y no
sustituye al CSV municipal, que se conserva tal cual.

Lee:
  - data/procesado/anuncios_vivienda_residencial_filtrado.csv (via helper unico)
  - data/procesado/esfuerzo_mercado_2026.csv (salario ajustado 2026)

Guarda:
  - data/resultados/esfuerzo_por_tipo_nivel_anuncio_2026.csv

Uso:
    python analysis/esfuerzo_por_tipo_nivel_anuncio.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "transform"))

from _anuncios_2026 import cargar_anuncios_2026, mediana_con_ic  # noqa: E402
from calcular_esfuerzo_mercado_2026_por_tipo import _tipo_de_vivienda  # noqa: E402

PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"
MERCADO = PROC / "esfuerzo_mercado_2026.csv"
OUT = RES / "esfuerzo_por_tipo_nivel_anuncio_2026.csv"

TIPOS = ("1-2 hab", "3 hab", "4+ hab")

CAVEAT = (
    "mediana a nivel de anuncio (no media de medianas municipales); "
    "ponderar por municipio daba cifras mas altas; ambas se conservan"
)


def _salarios() -> tuple[float, float]:
    """Salario joven ajustado 2026 (constante en el CSV municipal)."""
    d = pd.read_csv(MERCADO, encoding="utf-8-sig", dtype=str)
    s18 = pd.to_numeric(d["salario_joven_2026_ajustado_18_34_eur_mes"], errors="coerce")
    s16 = pd.to_numeric(d["salario_joven_2026_ajustado_16_29_eur_mes"], errors="coerce")
    return float(s18.median()), float(s16.median())


def main() -> int:
    df, meta = cargar_anuncios_2026()
    v = df[df["anuncio_valido"]].dropna(subset=["precio_eur", "habitaciones"]).copy()
    v["tipo_de_vivienda"] = v["habitaciones"].map(_tipo_de_vivienda)

    sal_18, sal_16 = _salarios()

    filas = []
    for tipo in TIPOS:
        precios = v.loc[v["tipo_de_vivienda"] == tipo, "precio_eur"].to_numpy(dtype=float)
        n = len(precios)
        ic18 = mediana_con_ic(precios / sal_18 * 100, semilla=20260101 + n)
        ic16 = mediana_con_ic(precios / sal_16 * 100, semilla=20260202 + n)
        filas.append({
            "tipo_de_vivienda": tipo,
            "n_anuncios": n,
            "salario_joven_2026_ajustado_18_34_eur_mes": round(sal_18, 2),
            "esfuerzo_mediana_anuncios_pct_18_34": round(ic18["mediana"], 2),
            "ic95_lo_pct_18_34": round(ic18["lo"], 2),
            "ic95_hi_pct_18_34": round(ic18["hi"], 2),
            "ic95_amplitud_pct_18_34": round(ic18["amplitud_pct"], 1),
            "esfuerzo_mediana_anuncios_pct_16_29": round(ic16["mediana"], 2),
            "metodo": "mediana de anuncios; IC95 % bootstrap percentil 2000 replicas",
            "caveat": CAVEAT,
        })

    out = pd.DataFrame(filas)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"OK: {OUT.name} ({len(out)} tipos, {meta['n_usados']} anuncios usados)")
    for _, r in out.iterrows():
        print(f"   {r['tipo_de_vivienda']:>8}: {r['esfuerzo_mediana_anuncios_pct_18_34']:6.1f} % "
              f"[{r['ic95_lo_pct_18_34']:.1f} - {r['ic95_hi_pct_18_34']:.1f}] "
              f"n={int(r['n_anuncios'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
