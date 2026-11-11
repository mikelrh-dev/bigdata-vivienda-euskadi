"""Sensibilidad del esfuerzo: IDW vs oficial y bootstrap de los 4 robustos.

Dos preguntas:
  1. Cuanto cambia el titular si se incluyen los 93 municipios con alquiler
     imputado por IDW en lugar de quedarse en los 159 oficiales.
  2. Cuanta incertidumbre tiene el esfuerzo de los 4 municipios con n>=30 si
     se remuestrean sus anuncios (precio de vivienda completa de larga
     estancia).

Salidas en data/resultados/:
  - sensibilidad_idw.csv
  - bootstrap_robustos.csv

No escribe en data/raw ni en Mongo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RESULTADOS_DIR  # noqa: E402

RES = RESULTADOS_DIR
PROC = PROCESADO_DIR

ROBUSTOS = {
    "48020": "Bilbao",
    "20069": "Donostia",
    "48044": "Getxo",
    "01059": "Vitoria-Gasteiz",
}
N_BOOT = 10_000
SEED = 42


def sensibilidad_idw() -> pd.DataFrame:
    df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv")
    df["codigo_ine"] = df["_id"].astype(str).str.zfill(5)
    esfuerzo = pd.to_numeric(df["esfuerzo_joven_pct_18_34"], errors="coerce")

    oficial = df["tiene_alquiler_oficial"].astype(str).str.lower().isin(["true", "1"])
    filas = []
    for etiqueta, mascara in (("oficial_159", oficial), ("idw_252", oficial | ~oficial)):
        valores = esfuerzo[mascara].dropna()
        filas.append(
            {
                "escenario": etiqueta,
                "n": len(valores),
                "mediana_esfuerzo_pct": round(float(valores.median()), 2),
                "n_sobre_30": int((valores > 30).sum()),
                "pct_sobre_30": round(float((valores > 30).mean() * 100), 1),
            }
        )
    return pd.DataFrame(filas)


def _precios_vivienda(codigo: str) -> np.ndarray:
    anuncios = pd.read_csv(PROC / "anuncios_unificados.csv", encoding="utf-8-sig")
    anuncios["codigo_ine"] = anuncios["codigo_ine"].astype(str).str.zfill(5)
    d = anuncios[anuncios["codigo_ine"] == codigo].copy()
    d = d[d["modalidad"].astype(str).str.lower().str.contains("larga")]
    d["precio_eur"] = pd.to_numeric(d["precio_eur"], errors="coerce")
    d["superficie_m2"] = pd.to_numeric(d["superficie_m2"], errors="coerce")
    d = d[(d["precio_eur"] > 0) & (d["superficie_m2"] >= 30)]
    if "es_outlier_iqr" in d.columns:
        d = d[~d["es_outlier_iqr"].astype(str).str.lower().isin(["true", "1"])]
    return d["precio_eur"].to_numpy(dtype=float)


def bootstrap_robustos() -> pd.DataFrame:
    renta = pd.read_csv(PROC / "analisis_variables_base.csv", encoding="utf-8-sig", dtype={"codigo_ine": str})
    renta["codigo_ine"] = renta["codigo_ine"].str.zfill(5)
    renta_joven = renta.set_index("codigo_ine")["renta_joven_estimada_18_34"]

    canonico_df = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv")
    canonico_df["codigo_ine"] = canonico_df["_id"].astype(str).str.zfill(5)
    canonico = canonico_df.set_index("codigo_ine")["esfuerzo_joven_pct_18_34"]

    rng = np.random.default_rng(SEED)
    filas = []
    for codigo, nombre in ROBUSTOS.items():
        precios = _precios_vivienda(codigo)
        if len(precios) == 0 or codigo not in renta_joven.index:
            continue
        base = float(renta_joven.loc[codigo])
        punto_canonico = float(canonico.loc[codigo])
        mediana_anuncios = float(np.median(precios))
        # El nivel lo fija Eustat (canonico); el bootstrap mide solo la
        # dispersion relativa de la muestra de anuncios.
        muestras = np.empty(N_BOOT)
        n = len(precios)
        for i in range(N_BOOT):
            remuestra = rng.choice(precios, size=n, replace=True)
            mediana_boot = float(np.median(remuestra))
            muestras[i] = punto_canonico * (mediana_boot / mediana_anuncios)
        filas.append(
            {
                "codigo_ine": codigo,
                "municipio": nombre,
                "n_anuncios_larga_vivienda": n,
                "esfuerzo_canonico_pct": round(punto_canonico, 2),
                "esfuerzo_anuncios_pct": round(mediana_anuncios * 12 / base * 100, 2),
                "ic95_inf": round(float(np.percentile(muestras, 2.5)), 2),
                "ic95_sup": round(float(np.percentile(muestras, 97.5)), 2),
                "amplitud_pp": round(float(np.percentile(muestras, 97.5) - np.percentile(muestras, 2.5)), 2),
            }
        )
    return pd.DataFrame(filas)


def main() -> int:
    sens = sensibilidad_idw()
    boot = bootstrap_robustos()
    sens.to_csv(RES / "sensibilidad_idw.csv", index=False, encoding="utf-8-sig")
    boot.to_csv(RES / "bootstrap_robustos.csv", index=False, encoding="utf-8-sig")
    print(sens.to_string(index=False))
    print()
    print(boot.to_string(index=False))
    print(f"\nSemilla {SEED}, {N_BOOT} remuestreos por municipio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
