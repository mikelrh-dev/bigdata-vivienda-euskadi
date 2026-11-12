"""Calcula esfuerzo de mercado 2026 por municipio y tipo de vivienda.

Combina:
  - precio de anuncio 2026 (desde anuncios_vivienda_residencial_filtrado.csv)
  - salario joven OVJ 2024 ajustado por factor IPC INE 2024->2026

Deriva tipo_de_vivienda de habitaciones:
  "1-2 hab" si habitaciones <= 2, "3 hab" si == 3, "4+ hab" si >= 4.

Esfuerzo = precio_mediana / salario_mensual_ajustado * 100 (misma formula que T-02).

NO toca raw ni esfuerzo canonico 2024.

Guarda:
    data/procesado/esfuerzo_mercado_2026_por_tipo.csv

Uso:
    python transform/calcular_esfuerzo_mercado_2026_por_tipo.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"

OUT = PROC / "esfuerzo_mercado_2026_por_tipo.csv"

ANUNCIOS = PROC / "anuncios_vivienda_residencial_filtrado.csv"
IPC = RAW / "ipc_ine_2024_2026.csv"
SALARIO = RAW / "ovj_salario_joven_2024.json"


def _load_ipc_factor() -> tuple[float, float, float, str]:
    """Carga IPC 2024, IPC 2026 y factor desde raw.

    Retorna (ipc_2024, ipc_2026, factor, flag).
    """
    if not IPC.exists():
        return 107.2, 117.8, 117.8 / 107.2, "fallback"
    df = pd.read_csv(IPC, dtype=str, encoding="utf-8-sig")
    fila_2024 = df[df["ano"].astype(str) == "2024"]
    fila_2026 = df[df["ano"].astype(str) == "2026"]
    fila_factor = df[df["ano"].astype(str) == "factor_2026_2024"]
    ipc_2024 = float(fila_2024["ipc_medio_anual"].iloc[0]) if len(fila_2024) else 107.2
    ipc_2026 = float(fila_2026["ipc_medio_anual"].iloc[0]) if len(fila_2026) else 117.8
    factor_doc = float(fila_factor["ipc_medio_anual"].iloc[0]) if len(fila_factor) else (ipc_2026 / ipc_2024)
    flag = str(fila_2024["flag"].iloc[0]) if len(fila_2024) else "fallback"
    return ipc_2024, ipc_2026, factor_doc, flag


def _load_salario_base() -> dict[str, float]:
    """Carga salario base OVJ 2024 por tramo desde raw."""
    with SALARIO.open(encoding="utf-8") as f:
        datos = json.load(f)
    out: dict[str, float] = {}
    for fila in datos.get("datos", []):
        tramo = str(fila["tramo_edad"])
        out[tramo] = float(fila["salario_neto_mes_eur"])
    return out


def _tipo_de_vivienda(habitaciones: float) -> str:
    """Deriva el tipo de vivienda a partir del numero de habitaciones."""
    if habitaciones <= 2:
        return "1-2 hab"
    if habitaciones == 3:
        return "3 hab"
    return "4+ hab"


def main() -> int:
    ipc_2024, ipc_2026, factor_ipc, flag_ipc = _load_ipc_factor()
    salario_base = _load_salario_base()

    salario_18_34_2024 = salario_base.get("18-34", 1564.0)
    salario_16_29_2024 = salario_base.get("16-29", 1381.0)

    salario_18_34_2026 = salario_18_34_2024 * factor_ipc
    salario_16_29_2026 = salario_16_29_2024 * factor_ipc

    if not ANUNCIOS.exists():
        print(f"Falta {ANUNCIOS.name}. Ejecuta primero generar_anuncios_residencial_filtrado.py")
        return 1

    df = pd.read_csv(ANUNCIOS, dtype=str, encoding="utf-8-sig")
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)
    df["precio_eur"] = pd.to_numeric(df["precio_eur"], errors="coerce")
    df["habitaciones"] = pd.to_numeric(df["habitaciones"], errors="coerce")

    # Solo filas con precio y habitaciones derivables.
    df = df.dropna(subset=["precio_eur", "habitaciones"]).copy()
    df["tipo_de_vivienda"] = df["habitaciones"].map(_tipo_de_vivienda)

    filas = []
    for (code, tipo), grupo in df.groupby(["codigo_ine", "tipo_de_vivienda"], sort=True):
        precios = grupo["precio_eur"].dropna().tolist()
        n_anuncios = len(precios)
        if n_anuncios == 0:
            continue
        precios_sorted = sorted(precios)
        n = len(precios_sorted)
        mediana = (
            precios_sorted[n // 2]
            if n % 2 == 1
            else (precios_sorted[n // 2 - 1] + precios_sorted[n // 2]) / 2
        )
        esfuerzo_18_34 = mediana / salario_18_34_2026 * 100
        esfuerzo_16_29 = mediana / salario_16_29_2026 * 100

        filas.append({
            "codigo_ine": code,
            "tipo_de_vivienda": tipo,
            "precio_mediana_eur": round(mediana, 2),
            "n_anuncios": n_anuncios,
            "salario_joven_2026_ajustado_18_34_eur_mes": round(salario_18_34_2026, 2),
            "salario_joven_2026_ajustado_16_29_eur_mes": round(salario_16_29_2026, 2),
            "esfuerzo_mercado_2026_pct_18_34": round(esfuerzo_18_34, 2),
            "esfuerzo_mercado_2026_pct_16_29": round(esfuerzo_16_29, 2),
            "factor_ipc": round(factor_ipc, 6),
            "vintage_numerador": 2026,
            "vintage_denominador": 2024,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame(filas, columns=[
        "codigo_ine", "tipo_de_vivienda", "precio_mediana_eur", "n_anuncios",
        "salario_joven_2026_ajustado_18_34_eur_mes",
        "salario_joven_2026_ajustado_16_29_eur_mes",
        "esfuerzo_mercado_2026_pct_18_34", "esfuerzo_mercado_2026_pct_16_29",
        "factor_ipc", "vintage_numerador", "vintage_denominador",
    ])
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(
        f"OK: {OUT.name} ({len(df_out)} grupos, "
        f"factor_ipc={factor_ipc}, flag_ipc={flag_ipc})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
