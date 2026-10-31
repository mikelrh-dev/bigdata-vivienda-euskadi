"""Recalcula la cobertura de anuncios por municipio desde datos deduplicados.

SEGUNDO y ultimo escritor autorizado de data/procesado/dim_municipios.csv
(el primero es dim_municipios.py). Motivo: dim_municipios.py corre ANTES de
la unificacion y solo puede contar filas crudas (843); este paso corre
DESPUES y cuenta anuncios unicos post-dedup (759), y recalcula
tipologia_mercado con el mismo umbral (>= 30).

Lee:
- data/procesado/dim_municipios.csv (n_anuncios crudo -> n_anuncios_raw)
- data/procesado/anuncios_unificados.csv (recuento real por codigo_ine)

Escribe: data/procesado/dim_municipios.csv (misma tabla + n_anuncios_raw).
No toca raw.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"


def _es_verdadero(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.lower().isin(["true", "1"])


def main() -> int:
    dim = pd.read_csv(PROC / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
    uni = pd.read_csv(PROC / "anuncios_unificados.csv", dtype=str, encoding="utf-8-sig")
    uni["codigo_ine"] = uni["codigo_ine"].str.zfill(5)
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)

    # Trazabilidad: conservar el recuento crudo antes de sustituirlo.
    dim["n_anuncios_raw"] = pd.to_numeric(dim["n_anuncios"], errors="coerce")
    real = uni.groupby("codigo_ine").size().rename("n_anuncios")
    dim = dim.drop(columns=["n_anuncios"]).merge(real, on="codigo_ine", how="left")
    dim["n_anuncios"] = dim["n_anuncios"].fillna(0).astype(int)

    con_alquiler = _es_verdadero(dim["tiene_alquiler_oficial"])
    con_fianzas = _es_verdadero(dim["tiene_fianzas_emal"])
    con_mercado = con_alquiler | con_fianzas
    dim["tipologia_mercado"] = np.select(
        [dim["n_anuncios"] >= 30, (dim["n_anuncios"] >= 1) & con_mercado],
        ["Nivel1_Mercado_Dinamico", "Nivel2_Mercado_Regulado"],
        default="Nivel3_Mercado_Rural_Cerrado")

    out = PROC / "dim_municipios.csv"
    dim.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"OK: {out} (suma n_anuncios={int(dim['n_anuncios'].sum())}, "
          f"raw={int(dim['n_anuncios_raw'].sum())})")
    print(dim["tipologia_mercado"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
