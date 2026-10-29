"""Calcula proxy de renta joven y esfuerzo min/max por municipio.

Fuentes:
- data/raw/eustat_renta_edad.csv: renta fiscal CAE por tramo de edad (2024)
- data/raw/ovj_salario_joven_2024.json: salario neto joven OVJ (2024)
- data/procesado/analisis_variables_base.csv: renta_personal_total, alquiler por municipio

Proxy fiscal (media simple de 3 tramos, sin ponderar por poblacion):
  ratio_fiscal = (1599 + 8156 + 20109) / 3 / 28170 = 0.353

Proxy salarial (OVJ 2024):
  ratio_salarial_18_34 = 1564*12 / 28170 = 0.666
  ratio_salarial_16_29 = 1381*12 / 28170 = 0.588

Guarda data/procesado/dim_municipios_enriquecido.csv.
No toca raw.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"

# Renta fiscal CAE por tramo (2024, sexo Total)
RENTA_18_19 = 1599
RENTA_20_24 = 8156
RENTA_25_29 = 20109
RENTA_TOTAL_CAE = 28170

# Salario neto joven OVJ 2024
SALARIO_18_34 = 1564
SALARIO_16_29 = 1381


def main() -> int:
    base = pd.read_csv(PROC / "analisis_variables_base.csv")

    # Proxy fiscal (media simple, sin ponderar por poblacion)
    ratio_fiscal = (RENTA_18_19 + RENTA_20_24 + RENTA_25_29) / 3 / RENTA_TOTAL_CAE

    # Proxy salarial
    ratio_sal_18_34 = (SALARIO_18_34 * 12) / RENTA_TOTAL_CAE
    ratio_sal_16_29 = (SALARIO_16_29 * 12) / RENTA_TOTAL_CAE

    out = base.copy()
    out["renta_joven_fiscal_proxy"] = out["renta_personal_total_eur"] * ratio_fiscal
    out["renta_joven_salarial_18_34"] = out["renta_personal_total_eur"] * ratio_sal_18_34
    out["renta_joven_salarial_16_29"] = out["renta_personal_total_eur"] * ratio_sal_16_29

    # Alquiler anual (cuantia media mensual * 12)
    out["alquiler_anual_calc"] = out["cuantia_media_eur_mes_media"] * 12

    # Esfuerzo: min (salarial, mayor renta -> menor esfuerzo), max (fiscal, menor renta -> mayor esfuerzo)
    out["esfuerzo_min_pct"] = out["alquiler_anual_calc"] / out["renta_joven_salarial_18_34"] * 100
    out["esfuerzo_max_pct"] = out["alquiler_anual_calc"] / out["renta_joven_fiscal_proxy"] * 100

    # Metadata
    out["ratio_fiscal"] = ratio_fiscal
    out["ratio_salarial_18_34"] = ratio_sal_18_34
    out["ratio_salarial_16_29"] = ratio_sal_16_29
    out["fuente_salario"] = "OVJ Irekia 2025-10-13 (salario neto 2024)"
    out["fuente_renta_fiscal"] = "Eustat renta_edad 2024 (CAE)"

    out_path = PROC / "dim_municipios_enriquecido.csv"
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"OK: {out_path} ({len(out)} filas, {len(out.columns)} cols)")
    print(f"ratio_fiscal={ratio_fiscal:.4f}, ratio_sal_18_34={ratio_sal_18_34:.4f}, ratio_sal_16_29={ratio_sal_16_29:.4f}")
    print(f"esfuerzo_min mediana={out['esfuerzo_min_pct'].median():.1f}%, esfuerzo_max mediana={out['esfuerzo_max_pct'].median():.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
