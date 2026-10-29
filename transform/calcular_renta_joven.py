"""Calcula proxy de renta joven y esfuerzo min/max por municipio.

Fuentes:
- data/raw/eustat_renta_edad.csv: renta fiscal CAE por tramo de edad (2024)
- data/raw/ovj_salario_joven_2024.json: salario neto joven OVJ (2024)
- data/procesado/analisis_variables_base.csv: renta_personal_total, alquiler por municipio
- data/raw/lanbide_paro_juvenil.csv: tasa de paro joven por municipio

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
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"


def _ratio_fiscal_desde_eustat() -> float:
    """Calcula ratio fiscal (media de tramos 18-19/20-24/25-29 vs total CAE) desde eustat_renta_edad.csv."""
    df = pd.read_csv(RAW / "eustat_renta_edad.csv")
    d = df[(df["sexo__etiqueta"] == "Total") & (df["tipo de renta__etiqueta"] == "Renta total")]
    d = d[d["periodo"] == 2024]
    tramos = {}
    for _, row in d.iterrows():
        etiqueta = str(row["edad__etiqueta"]).strip()
        valor = row["Renta personal media de la C.A. de Euskadi (euros)"]
        tramos[etiqueta] = valor
    r18_19 = tramos.get("De 18 a 19 años") or tramos.get("18 a 19 años")
    r20_24 = tramos.get("De 20 a 24 años") or tramos.get("20 a 24 años")
    r25_29 = tramos.get("De 25 a 29 años") or tramos.get("25 a 29 años")
    rtotal = tramos.get("Total") or tramos.get("Total (todas las edades)")
    if r18_19 is None or r20_24 is None or r25_29 is None or rtotal is None:
        r18_19, r20_24, r25_29, rtotal = 1599, 8156, 20109, 28170
    return (r18_19 + r20_24 + r25_29) / 3 / rtotal


RENTA_TOTAL_CAE = 28170

# Salario neto joven OVJ 2024
SALARIO_OVJ_18_34 = 1564
SALARIO_OVJ_18_29 = 1381


def main() -> int:
    base = pd.read_csv(PROC / "analisis_variables_base.csv")

    # Proxy fiscal (media simple, sin ponderar por poblacion) - ratio dinamico desde eustat
    ratio_fiscal = _ratio_fiscal_desde_eustat()

    # Proxy salarial
    ratio_sal_18_34 = (SALARIO_OVJ_18_34 * 12) / RENTA_TOTAL_CAE
    ratio_sal_18_29 = (SALARIO_OVJ_18_29 * 12) / RENTA_TOTAL_CAE

    out = base.copy()
    out["renta_joven_fiscal_proxy"] = out["renta_personal_total_eur"] * ratio_fiscal
    out["renta_joven_salarial_18_34"] = out["renta_personal_total_eur"] * ratio_sal_18_34
    out["renta_joven_salarial_16_29"] = out["renta_personal_total_eur"] * ratio_sal_18_29

    # Alquiler anual (cuantia media mensual * 12)
    out["alquiler_anual_calc"] = out["cuantia_media_eur_mes_media"] * 12

    # Esfuerzo: min (salarial, mayor renta -> menor esfuerzo), max (fiscal, menor renta -> mayor esfuerzo)
    out["esfuerzo_min_pct"] = out["alquiler_anual_calc"] / out["renta_joven_salarial_18_34"] * 100
    out["esfuerzo_max_pct"] = out["alquiler_anual_calc"] / out["renta_joven_fiscal_proxy"] * 100

    # Solucion 1+2 (aditivo): OVJ + Housing Wage
    out["salario_ovj_neto_mes"] = SALARIO_OVJ_18_29
    out["housing_wage_mes"] = out["cuantia_media_eur_mes_media"] / 0.30
    out["esfuerzo_ovj_individual_pct"] = (out["cuantia_media_eur_mes_media"] / SALARIO_OVJ_18_29) * 100
    out["esfuerzo_ovj_pareja_pct"] = (out["cuantia_media_eur_mes_media"] / (2 * SALARIO_OVJ_18_29)) * 100
    out["brecha_emancipacion_eur"] = out["housing_wage_mes"] - SALARIO_OVJ_18_29

    # Tarea 2: salario joven ajustado al riesgo local (paro joven Lanbide)
    paro = pd.read_csv(RAW / "lanbide_paro_juvenil.csv")[["codigo_ine", "tasa_paro_joven_pct"]]
    out = out.merge(paro, on="codigo_ine", how="left")
    paro_mean = out["tasa_paro_joven_pct"].mean()
    paro_std = out["tasa_paro_joven_pct"].std(ddof=0)
    z = (out["tasa_paro_joven_pct"] - paro_mean) / paro_std
    z = z.clip(-1.0, 1.0)
    factor = 1.0 - 0.15 * z
    out["salario_joven_ajustado_local_eur"] = (SALARIO_OVJ_18_29 * factor).round(2)
    out["esfuerzo_ajustado_pct"] = (out["cuantia_media_eur_mes_media"] / out["salario_joven_ajustado_local_eur"]) * 100

    # Metadata
    out["ratio_fiscal"] = ratio_fiscal
    out["ratio_salarial_18_34"] = ratio_sal_18_34
    out["ratio_salarial_16_29"] = ratio_sal_18_29
    out["fuente_salario"] = "OVJ Irekia 2025-10-13 (salario neto 2024) ajustado por paro joven Lanbide"
    out["fuente_renta_fiscal"] = "Eustat renta_edad 2024 (CAE)"

    out_path = PROC / "dim_municipios_enriquecido.csv"
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"OK: {out_path} ({len(out)} filas, {len(out.columns)} cols)")
    print(f"ratio_fiscal={ratio_fiscal:.4f}, ratio_sal_18_34={ratio_sal_18_34:.4f}, ratio_sal_18_29={ratio_sal_18_29:.4f}")
    print(f"esfuerzo_min mediana={out['esfuerzo_min_pct'].median():.1f}%, esfuerzo_max mediana={out['esfuerzo_max_pct'].median():.1f}%")
    print(f"esfuerzo_ovj_individual mediana={out['esfuerzo_ovj_individual_pct'].median():.1f}%, housing_wage mediana={out['housing_wage_mes'].median():.0f} EUR")
    print(f"salario_ajustado mediana={out['salario_joven_ajustado_local_eur'].median():.0f} EUR, esfuerzo_ajustado mediana={out['esfuerzo_ajustado_pct'].median():.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
