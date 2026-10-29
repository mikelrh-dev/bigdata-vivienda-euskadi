"""Calcula indice de tension social de demanda de vivienda (Etxebide + esfuerzo).

Genera/actualiza columnas en data/procesado/dim_municipios_enriquecido.csv:
- etxebide_solicitudes_por_mil_2024
- tension_demanda_social (0-100)
- tension_categoria (baja/media/alta)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"


def _percentil(series: pd.Series) -> pd.Series:
    return series.rank(pct=True) * 100


def main() -> int:
    dim = pd.read_csv(PROC / "dim_municipios_enriquecido.csv")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    etx = pd.read_csv(RAW / "etxebide_solicitudes.csv")
    etx24 = etx[etx["anio"] == 2024][["codigo_ine", "etxebide_solicitudes_por_mil"]].copy()
    etx24 = etx24.rename(columns={"etxebide_solicitudes_por_mil": "etxebide_solicitudes_por_mil_2024"})
    etx24["codigo_ine"] = etx24["codigo_ine"].astype(str).str.zfill(5)

    # imputar nulo con mediana (si hubiera)
    med = etx24["etxebide_solicitudes_por_mil_2024"].median()
    etx24["etxebide_solicitudes_por_mil_2024"] = etx24["etxebide_solicitudes_por_mil_2024"].fillna(med)

    dim = dim.merge(etx24, on="codigo_ine", how="left")
    dim["etxebide_solicitudes_por_mil_2024"] = dim["etxebide_solicitudes_por_mil_2024"].fillna(med)

    # percentiles
    p_sol = _percentil(dim["etxebide_solicitudes_por_mil_2024"])
    p_esf = _percentil(dim["esfuerzo_ovj_individual_pct"])
    dim["tension_demanda_social"] = ((p_sol + p_esf) / 2).round(1)

    def cat(v):
        if v < 33:
            return "baja"
        if v < 66:
            return "media"
        return "alta"

    dim["tension_categoria"] = dim["tension_demanda_social"].map(cat)

    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    out_path = PROC / "dim_municipios_enriquecido.csv"
    dim.to_csv(out_path, index=False, encoding="utf-8")
    print(f"OK: {out_path} ({len(dim)} filas, {len(dim.columns)} cols)")
    print(dim["tension_categoria"].value_counts().to_string())
    print(f"tension media={dim['tension_demanda_social'].median():.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
